import os
import uuid
from pypdf import PdfReader
from app.services.llm_service import ask_gemini

STORAGE_DIR = "pdf_storage"

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

async def process_pdf(file):
    try:
        pdf_id = str(uuid.uuid4())
        content = ""

        reader = PdfReader(file.file)
        for page in reader.pages:
            content += page.extract_text()

        file_path = os.path.join(STORAGE_DIR, f"{pdf_id}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return pdf_id
    except Exception as e:
        raise ValueError(f"Failed to process PDF: {str(e)}")

def get_pdf_content(pdf_id):
    try:
        file_path = os.path.join(STORAGE_DIR, f"{pdf_id}.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for PDF ID: {pdf_id}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        raise  # Re-raise FileNotFoundError directly
    except Exception as e:
        raise ValueError(f"Failed to read PDF content: {str(e)}")

async def generate_response(pdf_content, message):
    try:
        return await ask_gemini(pdf_content, message)
    except Exception as e:
        raise ValueError(f"Failed to generate response: {str(e)}")
