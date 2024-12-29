from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pypdf import PdfReader
from dotenv import load_dotenv
from io import BytesIO
from cachetools import TTLCache, cached
from db_funcs import save_pdf, get_pdf
import google.generativeai as genai
import os
import json


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# configure gemini
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Cache with a TTL of 10 minutes
cache = TTLCache(maxsize=1024, ttl=600)

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
    pdf_reader = PdfReader(BytesIO(file_content))
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

@cached(cache)
def generate_response(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response
    except genai.exceptions.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except genai.exceptions.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")

@app.post("/v1/{pdf_id}")
async def chat_with_pdf(request: Request, pdf_id: str):
    '''
    Expected request:
    {
        "message": "User message"
    }
    '''
    try:
        body = await request.json()
        user_message = body.get("message")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Message is required")

    # get pdf content
    name, content, metadata = get_pdf(pdf_id)

    prompt = f"""Respond to the message based on the given pdf file information. 
User's message: {user_message} 
File name: {name} 
File content: {content} 
File metadata: {metadata}"""

    response = generate_response(prompt)

    return {"response": response.text}