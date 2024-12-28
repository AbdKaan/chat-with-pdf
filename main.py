from fastapi import FastAPI, File, UploadFile, HTTPException, Request
import psycopg2
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2
from io import BytesIO
import json
import uuid


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432",
}

def save_pdf(name: str, content: str, metadata: dict):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        new_uuid = uuid.uuid4()
        uuid_str = str(new_uuid)

        # Insert file into database
        cursor.execute(
            "INSERT INTO pdf_files (id, name, content, metadata) VALUES (%s, %s, %s, %s) RETURNING id",
            (uuid_str, name, content, metadata),
        )

        # Fetch the id
        id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_pdf(id: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT name, content, metadata FROM pdf_files WHERE id=%s", (id,))
        pdf = cursor.fetchone()

        if not pdf:
            raise HTTPException(status_code=404, detail="PDF not found")

        conn.commit()
        cursor.close()
        conn.close()

        return pdf
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/v1/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Check if the file is pdf
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    # Check file size
    file.file.seek(0, os.SEEK_END)
    # Get the current position of the file pointer which is the file size in bytes
    file_size = file.file.tell()
    file.file.seek(0)  # Reset the file pointer to the beginning

    if file_size > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 10 MB.")

    # Content
    file_content = await file.read()
    pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    # Metadata
    json_metadata = json.dumps(pdf_reader.metadata)

    # Save to database and return the id
    id = save_pdf(file.filename, text, json_metadata)

    return {"pdf_id": id}

@app.post("/v1/{pdf_id}")
async def chat_with_pdf(pdf_id: str, request: Request):
    '''
    Expected request:
    {
        "message": "User message"
    }
    '''
    body = await request.json()
    user_message = body.get("message")

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    # configure gemini
    api_key = os.getenv("API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # get pdf content
    name, content, metadata = get_pdf(pdf_id)

    prompt = f"""Respond to the message based on the given pdf file information. 
User's message: {user_message} 
File name: {name} 
File content: {content} 
File metadata: {metadata}"""

    response = model.generate_content(prompt)

    return {"response": response.text}