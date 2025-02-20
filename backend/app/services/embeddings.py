import faiss
import numpy as np
import openai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

VECTOR_DB_PATH = "vector_db/faiss_index"
CHUNKS_PATH = "vector_db/chunks.json"  # Store chunks separately

def get_embedding(text: str):
    """Generates embeddings using OpenAI's text-embedding-ada-002."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response["data"][0]["embedding"], dtype="float32")

def split_text(text: str, chunk_size=500):
    """Splits text into manageable chunks for FAISS indexing."""
    words = text.split()
    return [" ".join(words[i: i + chunk_size]) for i in range(0, len(words), chunk_size)]

def process_and_store_embeddings(extracted_text: str, filename: str):
    """Generates embeddings from extracted text and updates FAISS."""
    
    text_chunks = []  # Store text chunks
    embeddings = []

    chunks = split_text(extracted_text)

    for chunk in chunks:
        text_chunks.append({"filename": filename, "chunk": chunk})
        embeddings.append(get_embedding(chunk))

    if not embeddings:
        print("⚠️ No text found for embeddings!")
        return

    # Convert new embeddings to NumPy array
    embeddings = np.array(embeddings, dtype="float32")

    # Load existing FAISS index if available
    index = None
    if os.path.exists(VECTOR_DB_PATH):
        index = faiss.read_index(VECTOR_DB_PATH)
    else:
        index = faiss.IndexFlatL2(embeddings.shape[1])

    # Add new embeddings to the index
    index.add(embeddings)

    # Save updated FAISS index
    faiss.write_index(index, VECTOR_DB_PATH)

    # Append new chunks to existing ones
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "r+", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_data.extend(text_chunks)
            f.seek(0)
            json.dump(existing_data, f, indent=4)
    else:
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(text_chunks, f, indent=4)

    print(f"✅ FAISS index updated with {len(text_chunks)} new chunks!")
