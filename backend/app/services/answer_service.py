from typing import Any


def build_grounded_prompt(
    question: str,
    search_results: list[dict[str, Any]],
) -> str:
    if not search_results:
        return f"""
You are an internal support assistant.

The approved knowledge base does not contain enough information to answer this question.

Question:
{question}

Respond exactly:
"I couldn't find enough information in the approved knowledge base."
""".strip()

    context_sections = []

    for result in search_results:
        context_sections.append(
            f"""
Source: {result["source"]}
Chunk: {result["chunk_index"]}
Relevance score: {result["score"]}

Content:
{result["content"]}
""".strip()
        )

    context = "\n\n---\n\n".join(context_sections)

    return f"""
You are SupportFlow AI, an internal support assistant.

Answer the user's question using only the approved knowledge-base context below.

Rules:
1. Do not use outside knowledge.
2. Do not invent missing details.
3. If the context is insufficient, say:
   "I couldn't find enough information in the approved knowledge base."
4. Keep the answer concise and clear.
5. Format multiple requirements as a numbered or bulleted Markdown list.
6. Do not include a title or heading such as
   "Answer", "# Answer", or "## Answer".
   Start directly with the response.
7. Do not include source citations inside the answer.
   The application displays sources separately.

Approved knowledge-base context:
{context}

User question:
{question}
""".strip()