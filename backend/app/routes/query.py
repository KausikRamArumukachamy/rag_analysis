from fastapi import APIRouter, HTTPException, Query
from app.services.query import search_faiss, generate_response
import os

router = APIRouter()

VECTOR_DB_PATH = "vector_db/faiss_index"

@router.get("/query/")
async def query_text(user_query: str = Query(..., title="User Query", description="Enter your search query")):
    """Handles user queries, searches FAISS, and generates a response."""

    # Ensure FAISS index exists
    if not os.path.exists(VECTOR_DB_PATH):
        raise HTTPException(status_code=500, detail="FAISS index not found. Run embeddings.py first!")

    # Search FAISS for relevant chunks
    results = search_faiss(user_query, top_k=3)

    if results:
        # Generate response using GPT
        final_answer = generate_response(user_query, results)
        return {
            "query": user_query,
            "ai_response": final_answer
        }
    else:
        raise HTTPException(status_code=404, detail="No relevant information found!")
