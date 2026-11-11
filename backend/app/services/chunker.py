from dataclasses import dataclass

from .document_loader import LoadedDocument


@dataclass
class DocumentChunk:
    source: str
    chunk_index: int
    content: str


def chunk_document(
    document: LoadedDocument,
    max_characters: int = 700,
) -> list[DocumentChunk]:
    lines = document.content.splitlines()

    sections: list[str] = []
    current_section: list[str] = []

    for line in lines:
        if line.startswith("#") and current_section:
            sections.append("\n".join(current_section).strip())
            current_section = []

        current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section).strip())

    chunks: list[DocumentChunk] = []

    for section in sections:
        if not section:
            continue

        if len(section) <= max_characters:
            chunks.append(
                DocumentChunk(
                    source=document.source,
                    chunk_index=len(chunks),
                    content=section,
                )
            )
            continue

        paragraphs = section.split("\n\n")
        current_content = ""

        for paragraph in paragraphs:
            candidate = (
                f"{current_content}\n\n{paragraph}"
                if current_content
                else paragraph
            )

            if len(candidate) > max_characters and current_content:
                chunks.append(
                    DocumentChunk(
                        source=document.source,
                        chunk_index=len(chunks),
                        content=current_content.strip(),
                    )
                )
                current_content = paragraph
            else:
                current_content = candidate

        if current_content:
            chunks.append(
                DocumentChunk(
                    source=document.source,
                    chunk_index=len(chunks),
                    content=current_content.strip(),
                )
            )

    return chunks