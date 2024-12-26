from fastapi import FastAPI, File, UploadFile, HTTPException
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

def main():
    api_key = os.getenv("API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Explain how AI works")
    print(response.text)

#main()

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

@app.post("/v1/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

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

    id = save_pdf(file.filename, text, json_metadata)
    return {"pdf_id": id}

@app.post("/v1/{pdf_id}")
async def chat_with_pdf():
    pass