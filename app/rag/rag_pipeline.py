import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

CHROMA_DB_DIRECTORY = "chroma_db"


def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


def create_embeddings(texts):
    embeddings = embedding_model.encode(texts)

    return embeddings


def store_in_chroma(chunks, document_id):
    texts = [chunk.page_content for chunk in chunks]

    embeddings = create_embeddings(texts)

    chroma_db = Chroma(
        persist_directory=CHROMA_DB_DIRECTORY,
        embedding_function=None
    )

    ids = [
        f"{document_id}_{index}"
        for index in range(len(texts))
    ]

    metadata = [
        {"document_id": str(document_id)}
        for _ in texts
    ]

    chroma_db._collection.add(
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadata,
        ids=ids
    )

    chroma_db.persist()


def semantic_search(query, top_k=5):
    chroma_db = Chroma(
        persist_directory=CHROMA_DB_DIRECTORY,
        embedding_function=None
    )

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = chroma_db._collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


def remove_document_embeddings(document_id):
    chroma_db = Chroma(
        persist_directory=CHROMA_DB_DIRECTORY,
        embedding_function=None
    )

    collection = chroma_db._collection

    data = collection.get()

    ids_to_delete = []

    for index, metadata in enumerate(data["metadatas"]):
        if metadata["document_id"] == str(document_id):
            ids_to_delete.append(
                data["ids"][index]
            )

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)