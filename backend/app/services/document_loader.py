from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoadedDocument:
    source: str
    content: str


def load_markdown_documents(directory: Path) -> list[LoadedDocument]:
    documents: list[LoadedDocument] = []

    for file_path in sorted(directory.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if content:
            documents.append(
                LoadedDocument(
                    source=file_path.name,
                    content=content,
                )
            )

    return documents