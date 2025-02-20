from fastapi import APIRouter, UploadFile, File
import os
import tempfile
from app.services.process_pdf import extract_text_from_pdf
from app.services.embeddings import process_and_store_embeddings
from app.services.google_drive import upload_to_drive

router = APIRouter()

@router.post("/upload/")
async def upload_report(file: UploadFile = File(...)):
    """Handles PDF upload, text extraction, and processing in a temp folder."""

    # Step 1: Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)

        # Step 2: Save the file temporarily
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        # Step 3: Extract text from the temporary file
        extracted_text = extract_text_from_pdf(temp_file_path)

        # Step 5: Process embeddings with extracted text
        process_and_store_embeddings(extracted_text, file.filename)

        # Step 6: Upload the PDF to Google Drive
        drive_file_id = await upload_to_drive(file)

    # The temporary directory is deleted automatically after the "with" block ends

    return {
        "filename": file.filename,
        "message": "File uploaded, processed, and text extracted successfully",
        "google_drive_file_id": drive_file_id
    }
