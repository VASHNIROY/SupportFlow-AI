export interface SourceCitation {
  source: string;
  chunk_index: number;
  score: number;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: SourceCitation[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function askQuestion(
  question: string,
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      top_k: 3,
    }),
  });

  if (!response.ok) {
    throw new Error("Unable to get an answer from SupportFlow AI.");
  }

  return response.json() as Promise<AskResponse>;
}