import ollama


MODEL_NAME = "llama3.2:3b"


def generate_answer(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.message.content