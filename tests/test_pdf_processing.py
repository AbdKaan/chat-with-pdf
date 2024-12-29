import pytest
from io import BytesIO
from pypdf import PdfReader, PdfWriter, PageObject


def test_extract_text_from_pdf():
    # Create a sample PDF content
    pdf_content = BytesIO()
    pdf_writer = PdfWriter()
    pdf_writer.add_page(PageObject.create_blank_page(width=72, height=72))
    pdf_writer.write(pdf_content)
    pdf_content.seek(0)

    # Read the PDF content
    pdf_reader = PdfReader(pdf_content)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    assert text == "", "The extracted text should be empty for a blank page."

# Run the tests
if __name__ == "__main__":
    pytest.main()