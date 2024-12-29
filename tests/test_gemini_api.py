import pytest
from unittest.mock import patch
import google.generativeai as genai


@patch("google.generativeai.GenerativeModel.generate_content")
def test_generate_response(mock_generate_content):
    mock_generate_content.return_value.text = "Mock response"
    prompt = "Test prompt"
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    assert response.text == "Mock response", "The response should match the mock response."

# Run the tests
if __name__ == "__main__":
    pytest.main()