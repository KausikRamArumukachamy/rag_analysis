from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from app.routes import upload, query
from app.utils.keep_alive import keep_server_alive
import os
import json
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

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

# Google Drive folder ID where files should be stored (update this with your folder ID)
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Load environment variables
load_dotenv()

# Load JSON credentials from environment variable
service_account_info = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
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
    """Fetches the list of uploaded files from Google Drive"""
    
    try:
        query = f"'{DRIVE_FOLDER_ID}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(name)", pageSize=100).execute()
        files = results.get("files", [])
        file_names = [file["name"] for file in files]
        return {"files": file_names}
    
    except Exception as e:
        logging.error(f"Error fetching file list: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching file list: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
