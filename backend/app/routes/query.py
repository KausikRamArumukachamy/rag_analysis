from fastapi import APIRouter, HTTPException, Query
from app.services.query import search_pinecone, generate_response  # ✅ Correct imports
import os

router = APIRouter()

@router.get("/query/")
async def query_text(user_query: str = Query(..., title="User Query", description="Enter your search query")):
    """Handles user queries, searches Pinecone, and generates a response."""

    # Search Pinecone for relevant chunks
    results = search_pinecone(user_query, top_k=3)  # ✅ Use Pinecone instead of FAISS

    if results:
        # Generate response using GPT
        final_answer = generate_response(user_query, results)
        return {
            "query": user_query,
            "ai_response": final_answer
        }
    else:
        raise HTTPException(status_code=404, detail="No relevant information found!")
