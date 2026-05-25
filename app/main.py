from fastapi import FastAPI

app = FastAPI(title="Financial RAG System")


@app.get("/")
def home():
    return {"message": "Financial RAG System API is running"}