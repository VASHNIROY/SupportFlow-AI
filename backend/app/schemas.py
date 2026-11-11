from pydantic import BaseModel, Field


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