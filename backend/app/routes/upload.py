from fastapi import APIRouter, UploadFile, File
import os
from app.services.process_pdf import extract_text_from_pdf
from app.services.embeddings import process_and_store_embeddings

router = APIRouter()

UPLOAD_DIR = "uploaded_reports"
TEXT_DIR = "processed_text"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_report(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text from the uploaded PDF
    extracted_text = extract_text_from_pdf(file_path)
    
    # Save extracted text
    text_file_path = os.path.join(TEXT_DIR, f"{file.filename}.txt")
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(extracted_text)

    # Automatically process and store embeddings
    process_and_store_embeddings()

    return {
        "filename": file.filename,
        "message": "File uploaded and processed successfully",
        "text_saved": text_file_path
    }
