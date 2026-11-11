from typing import Any

import ollama
from sqlalchemy import Engine, text


EMBEDDING_MODEL = "nomic-embed-text"


class PostgresRetriever:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @staticmethod
    def _embedding_to_pgvector(
        embedding: list[float],
    ) -> str:
        values = ",".join(str(value) for value in embedding)
        return f"[{values}]"

    def _create_embedding(self, text_value: str) -> list[float]:
        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=text_value,
        )

        return response.embeddings[0]

    def search(
        self,
        query: str,
        top_k: int = 3,
        minimum_score: float = 0.68,
    ) -> list[dict[str, Any]]:
        query_embedding = self._create_embedding(query)
        query_vector = self._embedding_to_pgvector(query_embedding)

        statement = text(
            """
            SELECT
                source,
                chunk_index,
                content,
                1 - (
                    embedding
                    <=> CAST(:query_embedding AS vector)
                ) AS score
            FROM document_chunks
            WHERE 1 - (
                embedding
                <=> CAST(:query_embedding AS vector)
            ) >= :minimum_score
            ORDER BY embedding  <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )

        with self.engine.connect() as connection:
            rows = connection.execute(
                statement,
                {
                    "query_embedding": query_vector,
                    "minimum_score": minimum_score,
                    "top_k": top_k,
                },
            ).mappings().all()

        return [
            {
                "source": row["source"],
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "score": round(float(row["score"]), 4),
            }
            for row in rows
        ]