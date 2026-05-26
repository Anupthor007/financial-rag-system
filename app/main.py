from fastapi import FastAPI

from app.database import engine, Base

from app.routes.auth import router as auth_router
from app.routes.roles import router as role_router
from app.routes.documents import router as document_router
from app.routes.rag import router as rag_router

from app.models.user import User
from app.models.role import Role
from app.models.document import Document

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Financial RAG System")

app.include_router(auth_router)
app.include_router(role_router)
app.include_router(document_router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {
        "message": "Financial RAG System API is running"
    }