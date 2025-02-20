import faiss
import numpy as np
import openai
import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

VECTOR_DB_PATH = "vector_db/faiss_index"
TEXT_DIR = "processed_text"
CHUNKS_PATH = "vector_db/chunks.json"  # Store text chunks separately

def get_embedding(text: str):
    """Generates embeddings using OpenAI's text-embedding-ada-002."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response["data"][0]["embedding"], dtype="float32")

def load_faiss_index():
    """Loads FAISS index."""
    return faiss.read_index(VECTOR_DB_PATH)

def load_text_chunks():
    """Loads text chunks from a JSON file."""
    if not os.path.exists(CHUNKS_PATH):
        return []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)  # Returns a list of dictionaries

def search_faiss(query: str, top_k=3):
    """Search FAISS for the most relevant chunks."""
    index = load_faiss_index()
    text_chunks = load_text_chunks()  # Load stored text chunks
    
    if not text_chunks:
        print("⚠️ No text chunks found. Please run embeddings.py first.")
        return []

    query_embedding = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in indices[0]:
        if i < len(text_chunks):
            results.append(text_chunks[i])  # Retrieve from JSON instead of metadata file

    return results

def generate_response(query: str, retrieved_docs: list):
    """Generates a response using GPT-4 and extracts structured insights."""
    context = "\n".join([doc["chunk"] for doc in retrieved_docs])
    prompt = f"""
    Context:
    {context}

    Query: {query}

    Task: Generate a response along with a structured JSON object for visualization. 
    If applicable, include a comparison chart (bar/pie) with relevant labels and values.
    Strictly add chart values and labels only if the data is a numerical data or a historical data
    or a comparision of numerical values and set chartNeeded as True.

    Return the output in this format:
    {{"text": "Response here", 
        "chartNeeded": true/false,
        "chart": {{"type": "bar/pie", "data": {{"labels": [], "values": []}}}}}}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that provides structured insights."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return json.loads(response["choices"][0]["message"]["content"])  # Ensure JSON response


if __name__ == "__main__":
    # Step 1: Ensure FAISS index exists
    if not os.path.exists(VECTOR_DB_PATH):
        print("🔄 FAISS index not found. Run embeddings.py first!")
        exit()

    # Step 2: Accept user query
    query = input("Enter your search query: ")

    # Step 3: Search FAISS for relevant chunks
    results = search_faiss(query, top_k=3)

    if results:
        # print("\n🔍 Top Search Results:")
        # for i, res in enumerate(results, 1):
        #     print(f"\n📌 From: {res['filename']}\n{res['chunk']}\n")

        # Step 4: Generate response using GPT
        final_answer = generate_response(query, results)
        print("\n🤖 AI Response:\n", final_answer)
    else:
        print("❌ No relevant information found!")
