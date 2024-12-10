import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import shutil
from app.services.pdf_service import STORAGE_DIR

# Enable FastAPI debug mode for tests
app.debug = True

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    # Setup: Create storage directory if it doesn't exist
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    
    yield
    
    # Cleanup: Remove test files and storage directory
    if os.path.exists("test_document.pdf"):
        os.remove("test_document.pdf")
    # Clean up any files in storage directory
    for file in os.listdir(STORAGE_DIR):
        os.remove(os.path.join(STORAGE_DIR, file))

def test_upload_pdf():
    # Copy the sample PDF file to test location
    shutil.copy("tests/sample.pdf", "test_document.pdf")
    
    # Send PDF file in multipart/form-data request
    with open("test_document.pdf", "rb") as pdf_file:
        files = {"file": ("test_document.pdf", pdf_file, "application/pdf")}
        response = client.post("/v1/pdf", files=files)
    
    # Print error details if status is 500
    if response.status_code == 500:
        print(f"Response body: {response.text}")
        print(f"Response headers: {response.headers}")
    
    # Assert response
    assert response.status_code == 201
    json_response = response.json()
    assert "pdf_id" in json_response

def test_chat_with_pdf():
    # First upload a PDF to get pdf_id
    shutil.copy("tests/sample.pdf", "test_document.pdf")
    
    with open("test_document.pdf", "rb") as pdf_file:
        files = {"file": ("test_document.pdf", pdf_file, "application/pdf")}
        upload_response = client.post("/v1/pdf", files=files)
    
    pdf_id = upload_response.json()["pdf_id"]
    
    # Test chat endpoint
    chat_input = {
        "message": "What is the main topic of the document?"
    }
    response = client.post(f"/v1/chat/{pdf_id}", json=chat_input)
    
    assert response.status_code == 200
    json_response = response.json()
    assert "response" in json_response
    assert isinstance(json_response["response"], str)

def test_invalid_pdf_upload():
    # Test with non-PDF file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write("This is not a PDF")
    
    with open(test_file_path, "rb") as file:
        files = {"file": ("test_document.txt", file, "text/plain")}
        response = client.post("/v1/pdf", files=files)
    
    os.remove(test_file_path)
    assert response.status_code == 400

def test_chat_with_invalid_pdf_id():
    # Test chat with non-existent PDF
    chat_input = {
        "message": "What is this document about?"
    }
    response = client.post("/v1/chat/nonexistent_id", json=chat_input)
    
    # Print error details if status is not 404
    if response.status_code != 404:
        print(f"Response body: {response.text}")
        print(f"Response headers: {response.headers}")
    
    assert response.status_code == 404

def test_chat_with_invalid_message():
    # First upload a valid PDF to get a real pdf_id
    shutil.copy("tests/sample.pdf", "test_document.pdf")
    
    with open("test_document.pdf", "rb") as pdf_file:
        files = {"file": ("test_document.pdf", pdf_file, "application/pdf")}
        upload_response = client.post("/v1/pdf", files=files)
    
    pdf_id = upload_response.json()["pdf_id"]
    
    # Test with empty message
    chat_input = {
        "message": ""
    }
    response = client.post(f"/v1/chat/{pdf_id}", json=chat_input)
    assert response.status_code == 400
 