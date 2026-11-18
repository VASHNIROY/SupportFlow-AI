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

export type TicketStatus =
  | "pending_approval"
  | "created"
  | "in_progress"
  | "resolved"
  | "closed"
  | "cancelled";

export type TicketPriority = "low" | "medium" | "high" | "urgent";

export interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  category: string;
  priority: TicketPriority;
  status: TicketStatus;
  created_by: string;
  approved_by: string | null;
}

export interface TicketDraftRequest {
  title: string;
  description: string;
  category: string;
  priority: TicketPriority;
}

export interface TicketApprovalRequest {
  approved_by: string;
}

export interface TicketEvent {
  id: number;
  ticket_id: number;
  event_type: string;
  old_status: TicketStatus | null;
  new_status: TicketStatus | null;
  performed_by: string;
  details: Record<string, unknown> | null;
  created_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const ACCESS_TOKEN_KEY = "supportflow_access_token";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);

    throw new Error(
      errorBody?.detail ?? `Request failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string): Promise<void> {
  const formData = new URLSearchParams();

  formData.set("username", username);
  formData.set("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Invalid username or password.");
  }

  const data = (await response.json()) as TokenResponse;

  sessionStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
}

export function logout(): void {
  sessionStorage.removeItem("supportflow_access_token");
}

function getAuthHeaders(): HeadersInit {
  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY);

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export function isAuthenticated(): boolean {
  return Boolean(sessionStorage.getItem("supportflow_access_token"));
}

export async function askQuestion(question: string): Promise<AskResponse> {
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

export async function createTicketDraft(
  payload: TicketDraftRequest,
): Promise<Ticket> {
  const response = await fetch(`${API_BASE_URL}/tickets/draft`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Unable to create ticket draft.");
  }

  return response.json() as Promise<Ticket>;
}

export async function approveTicket(ticketId: number): Promise<Ticket> {
  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/approve`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
  });

  return handleResponse<Ticket>(response);
}

export async function listTickets(): Promise<Ticket[]> {
  const response = await fetch(`${API_BASE_URL}/tickets`);

  if (!response.ok) {
    throw new Error("Unable to load tickets.");
  }

  return response.json() as Promise<Ticket[]>;
}

export async function getTicketEvents(
  ticketId: number,
): Promise<TicketEvent[]> {
  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/events`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Unable to load ticket history.");
  }

  return response.json() as Promise<TicketEvent[]>;
}
