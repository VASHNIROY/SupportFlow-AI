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

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas import TicketCreateRequest, TicketResponse
from app.services.ticket_service import TicketService

from fastapi import Depends, HTTPException, status
from app.repositories.ticket_repository import TicketRepository

from app.schemas import (
    TicketResponse,
    TicketStatusUpdateRequest,
)

from app.schemas import (
    TicketApprovalRequest,
    TicketDraftRequest,
)
from fastapi import Depends, HTTPException, Query, status

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

@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    session: Session = Depends(get_db),
) -> TicketResponse:
    ticket_service = TicketService(
        repository=TicketRepository(),
    )

    ticket = ticket_service.get_ticket(
        session,
        ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return ticket


@app.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketResponse,
)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdateRequest,
    session: Session = Depends(get_db),
) -> TicketResponse:
    ticket_service = TicketService()

    try:
        ticket = ticket_service.update_ticket_status(
            session,
            ticket_id=ticket_id,
            new_status=payload.status,
            performed_by=payload.performed_by,
        )

        session.commit()
        session.refresh(ticket)

        return ticket

    except LookupError as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update ticket status.",
        ) from error


@app.post(
    "/tickets/draft",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_draft(
    payload: TicketDraftRequest,
    session: Session = Depends(get_db),
) -> TicketResponse:
    ticket_service = TicketService()

    try:
        ticket = ticket_service.create_ticket_draft(
            session,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            priority=payload.priority,
            created_by=payload.created_by,
        )

        session.commit()
        session.refresh(ticket)

        return ticket

    except Exception as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create ticket draft.",
        ) from error


@app.post(
    "/tickets/{ticket_id}/approve",
    response_model=TicketResponse,
)
def approve_ticket(
    ticket_id: int,
    payload: TicketApprovalRequest,
    session: Session = Depends(get_db),
) -> TicketResponse:
    ticket_service = TicketService()

    try:
        ticket = ticket_service.approve_ticket(
            session,
            ticket_id=ticket_id,
            approved_by=payload.approved_by,
        )

        session.commit()
        session.refresh(ticket)

        return ticket

    except LookupError as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to approve ticket.",
        ) from error

@app.get(
    "/tickets",
    response_model=list[TicketResponse],
)
def list_tickets(
    ticket_status: str | None = Query(
        default=None,
        alias="status",
        pattern=(
            "^(pending_approval|created|in_progress|"
            "resolved|closed|cancelled)$"
        ),
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db),
) -> list[TicketResponse]:
    ticket_service = TicketService()

    return ticket_service.list_tickets(
        session,
        status=ticket_status,
        limit=limit,
        offset=offset,
    )
