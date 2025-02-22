from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from app.routes import upload, query
from app.utils.keep_alive import keep_server_alive
import os
import json
from pinecone import Pinecone
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
import uuid

app = FastAPI(title="RAG Market Research Analysis")

# Include routes
app.include_router(upload.router)
app.include_router(query.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Google Drive folder ID where files should be stored (update this with your folder ID)
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Pine cone api key and index name
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "vector-db")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
except Exception as e:
    raise RuntimeError(f"Failed to connect to Pinecone index: {e}")

# Load Google Drive credentials
service_account_json = os.getenv("SERVICE_ACCOUNT_JSON")
if not service_account_json:
    raise ValueError("Missing SERVICE_ACCOUNT_JSON in environment variables.")

service_account_info = json.loads(service_account_json)
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

@app.get("/")
def home():
    return {"message": "Welcome to RAG-powered Report Analysis!"}

@app.get("/health")
async def health_check():
    """Health check endpoint for self-pinging"""
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Start the keep-alive ping task when FastAPI starts."""
    asyncio.create_task(keep_server_alive())  # Runs in the background

@app.get("/uploaded_files/")
def list_uploaded_files():
    """Fetches the list of uploaded files from Google Drive."""
    
    try:
        query = f"'{DRIVE_FOLDER_ID}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)", pageSize=100).execute()
        files = results.get("files", [])

        file_data = [{"id": file["id"], "name": file["name"]} for file in files]

        return {"files": file_data}

    except Exception as e:
        logging.error(f"Error fetching file list: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching file list: {str(e)}")

@app.delete("/delete_file/")
async def delete_file(file_id: str):
    """
    Deletes a file from Google Drive and removes its corresponding embeddings from Pinecone.
    
    Args:
        file_id (str): The Google Drive file ID of the PDF to delete.
    
    Returns:
        dict: Success message if deletion is successful.
    """
    try:
        # Retrieve the file name using the file_id
        response = drive_service.files().get(fileId=file_id, fields="name").execute()
        filename = response.get("name")

        if not filename:
            raise HTTPException(status_code=404, detail="File not found in Google Drive.")

        # Delete the PDF from Google Drive
        drive_service.files().delete(fileId=file_id).execute()
        print(f"PDF {file_id} ({filename}) deleted successfully from Google Drive.")

        # Search for the corresponding JSON metadata file
        json_filename = f"{filename}.json"
        query = f"'{DRIVE_FOLDER_ID}' in parents and trashed=false and name='{json_filename}'"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        json_files = response.get("files", [])

        if json_files:
            json_file_id = json_files[0]["id"]  # Get JSON file ID

            # Download JSON file and extract embedding IDs
            request = drive_service.files().get_media(fileId=json_file_id)
            json_data = json.loads(request.execute().decode("utf-8"))
            embedding_ids = json_data.get("embedding_ids", [])

            # Delete embeddings from Pinecone
            if embedding_ids:
                index.delete(ids=embedding_ids)
                print(f"Deleted {len(embedding_ids)} embeddings from Pinecone.")

            # Delete the JSON metadata file from Google Drive
            drive_service.files().delete(fileId=json_file_id).execute()
            print(f"Deleted JSON metadata file {json_file_id} from Google Drive.")

        return {"message": f"File {filename} (ID: {file_id}) and associated embeddings deleted successfully."}

    except Exception as e:
        logging.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
