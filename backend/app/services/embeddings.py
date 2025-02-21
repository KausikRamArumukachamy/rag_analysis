import openai
import os
import json
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "vector-db")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise ValueError("❌ Missing API Keys. Check your .env file!")

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists; create it if not
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536, 
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2"
        )
    )

# Connect to the index
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

def process_and_store_embeddings(extracted_text: str, filename: str):
    """Stores embeddings in Pinecone instead of FAISS."""
    
    chunks = split_text(extracted_text)
    vectors = []

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        vectors.append({
            "id": f"{filename}_{i}",
            "values": embedding,
            "metadata": {"filename": filename, "text": chunk}
        })

    if vectors:
        index.upsert(vectors)  # Upload to Pinecone
        print(f"✅ Pinecone index updated with {len(vectors)} new chunks!")
    else:
        print("⚠️ No text found for embeddings!")

if __name__ == "__main__":
    print("Run this module through FastAPI!")
