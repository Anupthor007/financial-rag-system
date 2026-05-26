from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)

app.include_router(auth_router)
app.include_router(role_router)
app.include_router(document_router)
app.include_router(rag_router)


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )