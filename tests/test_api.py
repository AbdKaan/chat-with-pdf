import pytest
from fastapi.testclient import TestClient
import sys
import os
import json

# Add the parent directory to the sys.path to find main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db_funcs import save_pdf, delete_pdf


client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_data():
    # Setup test data (executed before tests)
    test_meta_data = json.dumps({"author": "Test author"})
    pdf_id = save_pdf("test.pdf", "Test content", test_meta_data)
    yield pdf_id
    # Teardown test data (executed after tests)
    delete_pdf(pdf_id)

def test_upload_pdf():
    pdf_path = os.path.join(os.getcwd(), "tests", "test.pdf")
    with open(pdf_path, "rb") as pdf_file:
        response = client.post("/v1/pdf", files={"file": ("test.pdf", pdf_file, "application/pdf")})
    assert response.status_code == 200
    assert "pdf_id" in response.json()

def test_chat_with_pdf(setup_test_data):
    pdf_id = setup_test_data
    response = client.post(f"/v1/{pdf_id}", json={"message": "Test message"})
    assert response.status_code == 200
    assert "response" in response.json()

# Run the tests
if __name__ == "__main__":
    pytest.main()