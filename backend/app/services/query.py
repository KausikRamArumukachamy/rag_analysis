import openai
import os
import numpy as np
import json
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Connect to the existing index
index = pc.Index(PINECONE_INDEX_NAME)

def get_embedding(text: str):
    """Generates embeddings using OpenAI's text-embedding-ada-002."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response["data"][0]["embedding"], dtype="float32").tolist()

def search_pinecone(query: str, top_k=3):
    """Search Pinecone for the most relevant chunks."""
    query_embedding = get_embedding(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    return results["matches"] if "matches" in results else []

def generate_response(query: str, retrieved_docs: list):
    """Generates a response using GPT-4 and extracts structured insights."""
    context = "\n".join([doc["metadata"]["text"] for doc in retrieved_docs])
    prompt = f"""
    Context:
    {context}

    Query: {query}

    Task: Generate a response along with a structured JSON object for visualization.
    If applicable, include a comparison chart (bar/pie) with relevant labels and values.
    Strictly add chart values and labels only if the data is numerical or a historical comparison.
    Set chartNeeded as True only when relevant.

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

    return json.loads(response["choices"][0]["message"]["content"])

if __name__ == "__main__":
    query = input("Enter your search query: ")
    results = search_pinecone(query, top_k=3)

    if results:
        final_answer = generate_response(query, results)
        print("\n🤖 AI Response:\n", final_answer)
    else:
        print("❌ No relevant information found!")
