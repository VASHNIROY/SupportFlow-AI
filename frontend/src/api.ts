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
  created_by: string;
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


export async function createTicketDraft(
  payload: TicketDraftRequest,
): Promise<Ticket> {
  const response = await fetch(`${API_BASE_URL}/tickets/draft`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Unable to create ticket draft.");
  }

  return response.json() as Promise<Ticket>;
}


export async function approveTicket(
  ticketId: number,
  payload: TicketApprovalRequest,
): Promise<Ticket> {
  const response = await fetch(
    `${API_BASE_URL}/tickets/${ticketId}/approve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    throw new Error("Unable to approve ticket.");
  }

  return response.json() as Promise<Ticket>;
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
  const response = await fetch(
    `${API_BASE_URL}/tickets/${ticketId}/events`,
  );

  if (!response.ok) {
    throw new Error("Unable to load ticket history.");
  }

  return response.json() as Promise<TicketEvent[]>;
}
