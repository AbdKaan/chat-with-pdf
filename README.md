# Chat with PDF

Chat with PDF is a FastAPI-based application that allows users to upload PDF files, extract their content, and interact with the content using a generative AI (Gemini 1.5 flash) model.

## Features

- Upload PDF files and extract their content to chat with them
- Generate context-aware responses based on PDF content and user queries
- Cache responses to improve performance

## Requirements

- Python
- FastAPI
- PostgreSQL
- Gemini API

Rest are in `requirements.txt`.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/AbdKaan/chat-with-pdf.git
```

2. Create and activate a virtual environment. Example with pip:

```
python -m venv <envname>
source <envname>/bin/activate
```

3. Install the required packages:

```
pip install -r requirements.txt
```

4. Set up the environment variables:

Create a `.env` file in the root directory and add the following variables:

```
API_KEY=your_gemini_api_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
```

5. Start your PostgreSQL server 

6. Create the table for database

```
python create_table.py
```

## Usage

Run the FastAPI application:

```
fastapi dev main.py
```

## API Endpoints

### Upload PDF

- **URL**: `/v1/pdf`
- **Method**: `POST`
- **Description**: Upload a PDF file and extract its content.
- **Request**:
  - `file`: PDF file to be uploaded (multipart/form-data)
- **Response**:
  - `pdf_id`: ID of the uploaded PDF

### Chat with PDF

- **URL**: `/v1/{pdf_id}`
- **Method**: `POST`
- **Description**: Generate a response based on the PDF content and user query.
- **Request**:
  - `message`: User message (JSON)
- **Response**:
  - `response`: Generated response

## Testing

Run the tests:
```sh
pytest tests
```

Curl requests:

```sh
# Upload pdf
curl -X POST "http:localhost:8000/v1/pdf" \
-F "file=@/path/to/your/pdf/file.pdf"

# Chat with pdf
curl -X POST "http://localhost:8000/v1/{pdf_id}" \
-H "Content-Type: application/json" \
-d '{"message": "Explain the content of the PDF"}'
```

## ToDo
- Add logging
- Add CICD