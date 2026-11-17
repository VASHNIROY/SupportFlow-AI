import { useState, type SyntheticEvent } from "react";

import {
  approveTicket,
  createTicketDraft,
  getTicketEvents,
  type Ticket,
  type TicketEvent,
  type TicketPriority,
} from "../api";

const initialForm = {
  title: "",
  description: "",
  category: "general",
  priority: "medium" as TicketPriority,
};

export default function TicketPanel() {
  const [form, setForm] = useState(initialForm);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [events, setEvents] = useState<TicketEvent[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [error, setError] = useState("");

  function updateField(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function loadTicketEvents(ticketId: number) {
    const ticketEvents = await getTicketEvents(ticketId);
    setEvents(ticketEvents);
  }
  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const createdTicket = await createTicketDraft(form);
      setTicket(createdTicket);
      await loadTicketEvents(createdTicket.id);
      setForm(initialForm);
    } catch {
      setError("Unable to create ticket draft.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleApprove() {
    if (!ticket) {
      return;
    }

    setError("");
    setIsApproving(true);

    try {
      const approvedTicket = await approveTicket(ticket.id);

      setTicket(approvedTicket);
      await loadTicketEvents(approvedTicket.id);
    } catch {
      setError("Unable to approve ticket.");
    } finally {
      setIsApproving(false);
    }
  }

  return (
    <section className="ticket-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">WORKFLOW</p>
          <h2>Create a support ticket</h2>
          <p>Raise an issue for review and approval.</p>
        </div>
      </div>
      <h2>Create Support Ticket</h2>

      <form className="ticket-form" onSubmit={handleSubmit}>
        <div className="ticket-field ticket-field-wide">
          <label htmlFor="ticket-title">Title</label>
          <input
            id="ticket-title"
            value={form.title}
            onChange={(event) => updateField("title", event.target.value)}
            placeholder="Example: Unable to access deployment pipeline"
            required
            minLength={5}
            maxLength={200}
          />
        </div>

        <div className="ticket-field ticket-field-wide">
          <label htmlFor="ticket-description">Description</label>
          <textarea
            id="ticket-description"
            value={form.description}
            onChange={(event) => updateField("description", event.target.value)}
            placeholder="Describe the issue clearly..."
            required
            minLength={10}
            maxLength={5000}
          />
        </div>
        <div className="ticket-field">
          <label htmlFor="ticket-category">Category</label>
          <input
            id="ticket-category"
            value={form.category}
            onChange={(event) => updateField("category", event.target.value)}
            placeholder="Access"
            required
          />
        </div>

        <div className="ticket-field">
          <label htmlFor="ticket-priority">Priority</label>
          <select
            id="ticket-priority"
            value={form.priority}
            onChange={(event) =>
              updateField("priority", event.target.value as TicketPriority)
            }
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div className="ticket-actions">
          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Creating draft..." : "Create draft"}
          </button>
        </div>
      </form>

      {error && <p role="alert">{error}</p>}

      {ticket && (
        <div className="ticket-preview">
          <h3>Ticket Preview</h3>

          <p>
            <strong>Ticket:</strong> {ticket.ticket_number}
          </p>

          <p>
            <strong>Status:</strong> {ticket.status}
          </p>

          <p>{ticket.title}</p>
          <p>{ticket.description}</p>

          {ticket.status === "pending_approval" && (
            <button
              type="button"
              onClick={handleApprove}
              disabled={isApproving}
            >
              {isApproving ? "Approving..." : "Approve Ticket"}
            </button>
          )}
        </div>
      )}
      {events.length > 0 && (
        <div className="ticket-history">
          <h4>Ticket History</h4>

          <ol>
            {events.map((event) => (
              <li key={event.id}>
                <strong>{event.event_type}</strong>

                <span>
                  {event.old_status && <> {event.old_status} →</>}{" "}
                  {event.new_status}
                </span>

                <small>
                  by {event.performed_by} on{" "}
                  {new Date(event.created_at).toLocaleString()}
                </small>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
