from pathlib import Path

import ollama
from sqlalchemy import text

from app.services.chunker import chunk_document
from app.services.document_loader import load_markdown_documents
from app.database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"

EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(content: str) -> list[float]:
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=content,
    )

    return response.embeddings[0]


def embedding_to_pgvector(embedding: list[float]) -> str:
    values = ",".join(str(value) for value in embedding)
    return f"[{values}]"


def ingest_documents() -> None:
    documents = load_markdown_documents(DOCUMENTS_DIR)

    total_chunks = 0

    with engine.begin() as connection:
        for document in documents:
            chunks = chunk_document(document)

            for chunk in chunks:
                embedding = create_embedding(chunk.content)
                vector_value = embedding_to_pgvector(embedding)

                connection.execute(
                    text(
                        """
                        INSERT INTO document_chunks (
                            source,
                            chunk_index,
                            content,
                            embedding
                        )
                        VALUES (
                            :source,
                            :chunk_index,
                            :content,
                            CAST(:embedding AS vector)
                        )
                        ON CONFLICT (source, chunk_index)
                        DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding
                        """
                    ),
                    {
                        "source": chunk.source,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "embedding": vector_value,
                    },
                )

                total_chunks += 1

    print(f"Ingested {total_chunks} document chunks.")


if __name__ == "__main__":
    ingest_documents()