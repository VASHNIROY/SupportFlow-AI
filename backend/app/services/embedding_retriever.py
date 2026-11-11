from dataclasses import asdict
from typing import Any

import ollama
import numpy as np

from .chunker import DocumentChunk


EMBEDDING_MODEL = "nomic-embed-text"


class EmbeddingRetriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        self.embeddings = [
            self._create_embedding(chunk.content)
            for chunk in chunks
        ]

    def _create_embedding(self, text: str) -> list[float]:
        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=text,
        )

        return response.embeddings[0]

    @staticmethod
    def _cosine_similarity(
        first: list[float],
        second: list[float],
    ) -> float:
        first_vector = np.array(first)
        second_vector = np.array(second)

        denominator = (
            np.linalg.norm(first_vector)
            * np.linalg.norm(second_vector)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(first_vector, second_vector) / denominator
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        minimum_score: float = 0.68,
    ) -> list[dict[str, Any]]:
        query_embedding = self._create_embedding(query)

        scored_chunks = []

        for chunk, embedding in zip(
            self.chunks,
            self.embeddings,
        ):
            score = self._cosine_similarity(
                query_embedding,
                embedding,
            )

            if score >= minimum_score:
                scored_chunks.append(
                    {
                        **asdict(chunk),
                        "score": round(score, 4),
                    }
                )

        scored_chunks.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return scored_chunks[:top_k]