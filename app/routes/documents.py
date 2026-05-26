import os
import shutil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse

from app.utils.dependencies import (
    get_current_user,
    require_roles
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_FOLDER = "uploads"


@router.post("/upload")
def upload_document(
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: str = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    allowed_extensions = [".pdf"]

    file_extension = os.path.splitext(
        file.filename
    )[1]

    if file_extension.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_location = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_document = Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_path=file_location,
        uploaded_by=uploaded_by
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "message": "Document uploaded successfully",
        "document_id": new_document.id
    }


@router.get("/", response_model=list[DocumentResponse])
def get_all_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    documents = db.query(Document).all()

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["Admin"])
    )
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }


@router.get("/search/")
def search_documents(
    company_name: str = "",
    document_type: str = "",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Document)

    if company_name:
        query = query.filter(
            Document.company_name.ilike(
                f"%{company_name}%"
            )
        )

    if document_type:
        query = query.filter(
            Document.document_type.ilike(
                f"%{document_type}%"
            )
        )

    documents = query.all()

    return documents