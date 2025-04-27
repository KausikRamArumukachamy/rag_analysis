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

    Task: You are a friendly AI assitant who is warm to talk to(so identify the small talks and 
    reposnd accordingly).Generate a response along with a structured JSON object for visualization.
    If applicable, include a comparison chart (bar/pie) with relevant labels and values.
    Strictly add chart values and labels only if the data is numerical or a historical comparison.
    Set chartNeeded as True only when relevant.

    Return the output in this format:
    {{"text": "Response here", 
        "chartNeeded": true/false,
        "chart": {{"type": "bar/pie", "data": {{"labels": [], "values": []}}}}}}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that provides structured insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )

        # Get the content of the response
        content = response["choices"][0]["message"].get("content", "")

        # Check if the content is a valid JSON string
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON: {content}")
            parsed_content = {
                "text": "Sorry, I couldn't generate a structured response.Try Again",
                "chartNeeded": False,
                "chart": {}
            }
        
        return parsed_content

    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return {
            "text": "Sorry, there was an error processing your request. Please try again.",
            "chartNeeded": False,
            "chart": {}
        }

if __name__ == "__main__":
    query = input("Enter your search query: ")
    results = search_pinecone(query, top_k=3)

    if results:
        final_answer = generate_response(query, results)
        print("\n🤖 AI Response:\n", final_answer)
    else:
        print("❌ No relevant information found!")
