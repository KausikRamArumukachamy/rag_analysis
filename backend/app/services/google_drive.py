import os
import io
import json
import tempfile
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from fastapi import UploadFile

# Load environment variables
load_dotenv()

# Load JSON credentials from environment variable
service_account_info = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
)

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

def get_drive_service():
    """Authenticate with Google Drive API using a service account stored in an env variable."""
    return build("drive", "v3", credentials=credentials)

async def upload_to_drive(file: UploadFile):
    """Upload file to Google Drive and return its file ID."""
    service = get_drive_service()

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)

        # Save file temporarily in the temp directory
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        file_metadata = {
            "name": file.filename,
            "parents": [FOLDER_ID],  # Upload to the specified Google Drive folder
        }

        # Open the saved file for upload
        with open(temp_file_path, "rb") as file_stream:
            media = MediaIoBaseUpload(file_stream, mimetype="application/pdf")

            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

    return uploaded_file.get("id")

async def upload_json_to_drive(filename: str, json_data: dict):
    """Create a JSON file with the same name as the PDF and upload it to Google Drive."""
    service = get_drive_service()

    # Convert JSON data to a string and then to a BytesIO stream
    json_str = json.dumps(json_data, indent=4)
    json_stream = io.BytesIO(json_str.encode("utf-8"))

    file_metadata = {
        "name": f"{filename}.json",  # Match the PDF filename
        "parents": [FOLDER_ID],
        "mimeType": "application/json"
    }

    media = MediaIoBaseUpload(json_stream, mimetype="application/json")

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return uploaded_file.get("id")
