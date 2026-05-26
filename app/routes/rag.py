from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document

from app.rag.rag_pipeline import (
    load_pdf,
    split_documents,
    store_in_chroma,
    semantic_search,
    remove_document_embeddings
)

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/index-document/{document_id}")
def index_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    documents = load_pdf(document.file_path)

    chunks = split_documents(documents)

    store_in_chroma(
        chunks,
        document_id
    )

    return {
        "message": "Document indexed successfully"
    }


@router.post("/search")
def search_rag(query: str):
    results = semantic_search(query)

    return {
        "query": query,
        "results": results["documents"][0]
    }


@router.delete("/remove-document/{document_id}")
def remove_document(
    document_id: int
):
    remove_document_embeddings(document_id)

    return {
        "message": "Document embeddings removed successfully"
    }


@router.get("/context/{document_id}")
def get_document_context(
    document_id: int
):
    results = semantic_search(
        str(document_id),
        top_k=10
    )

    return {
        "document_id": document_id,
        "context": results["documents"][0]
    }