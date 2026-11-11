from dataclasses import asdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .chunker import DocumentChunk


class TfidfRetriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
        )

        self.matrix = self.vectorizer.fit_transform(
            chunk.content for chunk in chunks
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        minimum_score: float = 0.20,
    ) -> list[dict]:
        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            self.matrix,
        )[0]

        ranked_indexes = scores.argsort()[::-1]

        results = []

        for index in ranked_indexes:
            score = float(scores[index])

            if score < minimum_score:
                continue

            chunk = self.chunks[index]

            results.append(
                {
                    **asdict(chunk),
                    "score": round(score, 4),
                }
            )

            if len(results) == top_k:
                break

        return results