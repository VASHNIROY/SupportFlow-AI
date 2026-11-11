import { useState } from "react";
import { askQuestion, type AskResponse } from "./api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      return;
    }

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await askQuestion(trimmedQuestion);
      setResult(response);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="chat-card">
        <p className="eyebrow">INTERNAL KNOWLEDGE ASSISTANT</p>

        <h1>SupportFlow AI</h1>

        <p className="description">
          Ask questions about approved support documentation.
        </p>

        <form onSubmit={handleSubmit} className="question-form">
          <label htmlFor="question">Your question</label>

          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What must be completed before releasing an application?"
            rows={5}
          />

          <button type="submit" disabled={isLoading || !question.trim()}>
            {isLoading ? "Searching..." : "Ask SupportFlow AI"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        {result && (
          <section className="result">
            <h2>Answer</h2>
            <div className="answer-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.answer}
              </ReactMarkdown>
            </div>
            <h3>Sources</h3>

            {result.sources.length === 0 ? (
              <p>No approved source was found.</p>
            ) : (
              <ul>
                {result.sources.map((source) => (
                  <li key={`${source.source}-${source.chunk_index}`}>
                    {source.source} — chunk {source.chunk_index} (
                    {source.score.toFixed(3)})
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
