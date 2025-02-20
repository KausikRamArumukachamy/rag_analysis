from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from app.routes import upload, query
from app.utils.keep_alive import keep_server_alive  # Import the keep-alive function

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
