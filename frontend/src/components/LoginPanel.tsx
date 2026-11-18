import { useState } from "react";
import type { SyntheticEvent } from "react";
import { login } from "../api";

interface LoginPanelProps {
  onLoginSuccess: () => void;
}

export default function LoginPanel({
  onLoginSuccess,
}: LoginPanelProps) {
  const [username, setUsername] = useState("demo-user");
  const [password, setPassword] = useState("demo-password");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login(username, password);
      onLoginSuccess();
    } catch {
      setError("Invalid username or password.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="login-panel">
      <p className="eyebrow">SECURE ACCESS</p>
      <h2>Sign in to SupportFlow AI</h2>

      <form onSubmit={handleSubmit}>
        <label>
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>

        {error && <p className="form-error">{error}</p>}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </section>
  );
}
