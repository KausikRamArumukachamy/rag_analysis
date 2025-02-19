# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from pathlib import Path
# import os

# # Load the free embedding model
# # model = SentenceTransformer("all-MiniLM-L6-v2")

# model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# # Function to get text embeddings using sentence-transformers
# def get_embedding(text: str):
#     return model.encode(text).tolist()

# # Function to split text into smaller chunks
# def split_text(text: str, chunk_size=500):
#     words = text.split()  # Split into words
#     return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# # Function to process text and store embeddings in FAISS
# def process_and_store_embeddings(text_path: str, faiss_index_path: str):
#     text = Path(text_path).read_text(encoding="utf-8")
#     chunks = split_text(text)

#     # Get embeddings
#     embeddings = [get_embedding(chunk) for chunk in chunks]
#     embeddings = np.array(embeddings).astype("float32")

#     # Create FAISS index
#     index = faiss.IndexFlatL2(embeddings.shape[1])
#     index.add(embeddings)

#     # Ensure directory exists before saving
#     os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)

#     # Save FAISS index
#     faiss.write_index(index, faiss_index_path)
#     print("✅ Embeddings stored successfully using Sentence Transformers!")

# # Example usage
# if __name__ == "__main__":
#     process_and_store_embeddings("processed_text/report1.txt", "vector_db/faiss_index")




# import faiss
# import numpy as np
# import openai
# from pathlib import Path
# import os

# from dotenv import load_dotenv

# # Load .env file
# load_dotenv()


# # Load OpenAI API key from environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def get_embedding(text: str):
#     """Generates embeddings using OpenAI's text-embedding-ada-002."""
#     response = openai.Embedding.create(
#         model="text-embedding-ada-002",
#         input=text
#     )
#     return np.array(response["data"][0]["embedding"], dtype="float32")

# def split_text(text: str, chunk_size=500):
#     """Splits text into chunks for FAISS storage."""
#     words = text.split()
#     return [" ".join(words[i: i + chunk_size]) for i in range(0, len(words), chunk_size)]

# def process_and_store_embeddings(text_path: str, faiss_index_path: str):
#     """Processes text, generates embeddings using OpenAI, and stores them in FAISS."""
#     text = Path(text_path).read_text(encoding="utf-8")
#     chunks = split_text(text)

#     embeddings = np.array([get_embedding(chunk) for chunk in chunks]).astype("float32")

#     # Create FAISS index
#     index = faiss.IndexFlatL2(embeddings.shape[1])
#     index.add(embeddings)

#     os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)
#     faiss.write_index(index, faiss_index_path)
#     print("✅ Embeddings stored successfully with OpenAI!")

# # Example usage
# if __name__ == "__main__":
#     process_and_store_embeddings("processed_text/report1.txt", "vector_db/faiss_index")



import faiss
import numpy as np
import openai
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

VECTOR_DB_PATH = "vector_db/faiss_index"
TEXT_DIR = "processed_text"
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

def process_and_store_embeddings():
    """Processes only new text files, generates embeddings, and updates FAISS."""
    
    text_chunks = []  # To store newly processed chunks
    embeddings = []
    
    # Load existing chunks if available
    existing_chunks = {}
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            existing_chunks = {entry["filename"] for entry in json.load(f)}
    
    for text_file in os.listdir(TEXT_DIR):
        if text_file.endswith(".txt") and text_file not in existing_chunks:
            file_path = os.path.join(TEXT_DIR, text_file)
            text = Path(file_path).read_text(encoding="utf-8")
            chunks = split_text(text)

            for chunk in chunks:
                text_chunks.append({"filename": text_file, "chunk": chunk})
                embeddings.append(get_embedding(chunk))

    if not embeddings:
        print("⚠️ No new files found for embeddings!")
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
    with open(CHUNKS_PATH, "r+", encoding="utf-8") as f:
        existing_data = json.load(f)
        existing_data.extend(text_chunks)
        f.seek(0)
        json.dump(existing_data, f, indent=4)

    print(f"✅ FAISS index updated with {len(text_chunks)} new chunks!")


if __name__ == "__main__":
    process_and_store_embeddings()

