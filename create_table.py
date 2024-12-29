import psycopg2
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def create_table():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE pdf_files (
                id UUID PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error creating table:", e)

create_table()
