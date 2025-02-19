from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, query

app = FastAPI(title="RAG Market Research Analysis")

# Include routes
app.include_router(upload.router)
app.include_router(query.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to RAG-powered Report Analysis!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
