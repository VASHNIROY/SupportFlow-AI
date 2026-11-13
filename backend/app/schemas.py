from pydantic import BaseModel, Field
from typing import Literal
from pydantic import ConfigDict

class AskRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=500,
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class SourceCitation(BaseModel):
    source: str
    chunk_index: int
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceCitation]

class TicketPreviewRequest(BaseModel):
    request: str = Field(
        min_length=5,
        max_length=1000,
    )


class TicketPreviewResponse(BaseModel):
    action: str
    title: str
    description: str
    category: str
    priority: Literal["low", "medium", "high", "urgent"]
    requires_approval: bool


class TicketCreateRequest(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=200,
    )

    description: str = Field(
        min_length=10,
        max_length=5000,
    )

    category: str = Field(
        min_length=2,
        max_length=50,
    )

    priority: Literal["low", "medium", "high", "urgent"] = "medium"

    created_by: str = Field(
        min_length=3,
        max_length=255,
    )

    approved_by: str = Field(
        min_length=3,
        max_length=255,
    )


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_by: str
    approved_by: str | None
    model_config = ConfigDict(from_attributes=True)

class TicketStatusUpdateRequest(BaseModel):
    status: Literal[
        "in_progress",
        "resolved",
        "closed",
        "cancelled",
    ]

    performed_by: str = Field(
        min_length=3,
        max_length=255,
    )

class TicketDraftRequest(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=200,
    )

    description: str = Field(
        min_length=10,
        max_length=5000,
    )

    category: str = Field(
        min_length=2,
        max_length=50,
    )

    priority: Literal[
        "low",
        "medium",
        "high",
        "urgent",
    ] = "medium"

    created_by: str = Field(
        min_length=3,
        max_length=255,
    )


class TicketApprovalRequest(BaseModel):
    approved_by: str = Field(
        min_length=3,
        max_length=255,
    )
