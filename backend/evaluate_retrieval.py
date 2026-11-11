import json
from pathlib import Path

from app.services.chunker import chunk_document
from app.services.document_loader import load_markdown_documents
from app.services.embedding_retriever import EmbeddingRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
QUESTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "retrieval_questions.json"
)


def build_retriever() -> EmbeddingRetriever:
    documents = load_markdown_documents(DOCUMENTS_DIR)

    chunks = [
        chunk
        for document in documents
        for chunk in chunk_document(document)
    ]

    return EmbeddingRetriever(chunks)


def main() -> None:
    with QUESTIONS_FILE.open(encoding="utf-8") as file:
        questions = json.load(file)

    retriever = build_retriever()

    correct = 0
    total = len(questions)

    for item in questions:
        question = item["question"]
        expected_source = item["expected_source"]

        results = retriever.search(
            query=question,
            top_k=1,
        )

        actual_source = (
            results[0]["source"]
            if results
            else None
        )

        is_correct = actual_source == expected_source

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"[{status}] {question}")
        print(f"  Expected: {expected_source}")
        print(f"  Actual:   {actual_source}")

        if results:
            print(f"  Score:    {results[0]['score']}")

        print()

    accuracy = correct / total if total else 0

    print(f"Retrieval accuracy: {correct}/{total}")
    print(f"Accuracy percentage: {accuracy:.2%}")


if __name__ == "__main__":
    main()