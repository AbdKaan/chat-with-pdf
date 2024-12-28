from fastapi import HTTPException
from dotenv import load_dotenv
import psycopg2
import uuid
import os


# Load environment variables from .env file
load_dotenv()

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