from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Query, Request
from .services.document_loader import load_markdown_documents
from .services.chunker import chunk_document
from .services.embedding_retriever import EmbeddingRetriever
from .services.answer_service import build_grounded_prompt
from .services.llm_client import generate_answer
from .database import engine
from .services.postgres_retriever import PostgresRetriever
from .schemas import AskRequest, AskResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from sqlalchemy import text

from app.database import engine
import ollama

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to PostgreSQL vector store...")

    app.state.retriever = build_retriever()

    print("PostgreSQL vector retriever ready")
    
    yield

    app.state.retriever = None
    print("Application shutdown complete")

app = FastAPI(
    title="SupportFlow AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "data" / "documents"

def build_retriever() -> PostgresRetriever:

    return PostgresRetriever(engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "supportflow-api",
    }


@app.get("/documents")
def list_documents() -> dict:
    documents = load_markdown_documents(DOCUMENTS_DIR)

    return {
        "count": len(documents),
        "documents": [
            {
                "source": document.source,
                "characters": len(document.content),
            }
            for document in documents
        ],
    }

@app.get("/chunks")
def list_chunks() -> dict:
    documents = load_markdown_documents(DOCUMENTS_DIR)

    chunks = [
        chunk
        for document in documents
        for chunk in chunk_document(document)
    ]

    return {
        "count": len(chunks),
        "chunks": [
            {
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "characters": len(chunk.content),
                "content": chunk.content,
            }
            for chunk in chunks
        ],
    }

@app.get("/search")
def search_documents(
    request: Request,
    query: str = Query(min_length=2),
    top_k: int = Query(default=3, ge=1, le=10),
) -> dict:
    retriever = request.app.state.retriever

    results = retriever.search(
        query=query,
        top_k=top_k,
    )

    return {
        "query": query,
        "results": results,
    }


@app.get("/ask")
def ask_question(
    request: Request,
    question: str = Query(min_length=2),
    top_k: int = Query(default=3, ge=1, le=10),
) -> dict:
    retriever = request.app.state.retriever

    search_results = retriever.search(
        query=question,
        top_k=top_k,
    )

    if not search_results:
        return {
            "question": question,
            "answer": (
                "I couldn't find enough information "
                "in the approved knowledge base."
            ),
            "sources": [],
        }

    grounded_prompt = build_grounded_prompt(
        question=question,
        search_results=search_results,
    )

    answer = generate_answer(grounded_prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "source": result["source"],
                "chunk_index": result["chunk_index"],
                "score": result["score"],
            }
            for result in search_results
        ],
    }

@app.post("/ask", response_model=AskResponse)
def ask_question_post(request: AskRequest) -> AskResponse:
    retriever = app.state.retriever

    search_results = retriever.search(
        query=request.question,
        top_k=request.top_k,
    )

    if not search_results:
        return AskResponse(
            question=request.question,
            answer=(
                "I couldn't find enough information "
                "in the approved knowledge base."
            ),
            sources=[],
        )

    grounded_prompt = build_grounded_prompt(
        question=request.question,
        search_results=search_results,
    )

    answer = generate_answer(grounded_prompt)

    return AskResponse(
        question=request.question,
        answer=answer,
        sources=[
            {
                "source": result["source"],
                "chunk_index": result["chunk_index"],
                "score": result["score"],
            }
            for result in search_results
        ],
    )

@app.get("/ready")
def readiness_check() -> dict:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        ollama.list()

        return {
            "status": "ready",
            "database": "available",
            "ollama": "available",
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(error),
            },
        ) from error