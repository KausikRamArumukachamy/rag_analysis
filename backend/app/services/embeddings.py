import openai
import os
import json
import numpy as np
import uuid
import tempfile
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from fastapi import UploadFile
from app.services.google_drive import upload_json_to_drive

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "vector-db")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise ValueError("Missing API Keys. Check your .env file!")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536, 
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-west-2")
    )

index = pc.Index(PINECONE_INDEX_NAME)

def get_embedding(text: str):
    """Generates embeddings using OpenAI's text-embedding-ada-002."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response["data"][0]["embedding"]

def split_text(text: str, chunk_size=500):
    """Splits text into manageable chunks."""
    words = text.split()
    return [" ".join(words[i: i + chunk_size]) for i in range(0, len(words), chunk_size)]

async def process_and_store_embeddings(extracted_text: str, filename: str):
    """Stores embeddings in Pinecone & saves IDs in Google Drive."""
    
    chunks = split_text(extracted_text)
    vectors = []
    embedding_ids = []

    unique_id = str(uuid.uuid4())  # Generate unique ID for this file

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        embedding_id = f"{filename}_{unique_id}_{i}"  # Unique ID per chunk

        vectors.append({
            "id": embedding_id,
            "values": embedding,
            "metadata": {"filename": filename, "text": chunk, "upload_id": unique_id}
        })

        embedding_ids.append(embedding_id)  # Store ID for deletion tracking

    if vectors:
        index.upsert(vectors)  # Upload to Pinecone
        print(f"Pinecone index updated with {len(vectors)} new chunks for {filename} (ID: {unique_id})!")

        # Store embedding IDs in a JSON file
        embeddings_metadata = {"filename": filename, "embedding_ids": embedding_ids}
        
        uploaded_json_id = await upload_json_to_drive(filename, embeddings_metadata)
        
        print(f"Embedding IDs stored in Google Drive (File ID: {uploaded_json_id})")

    else:
        print("No text found for embeddings!")

if __name__ == "__main__":
    print("Run this module through FastAPI!")
