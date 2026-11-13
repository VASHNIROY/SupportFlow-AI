from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketEvent
from app.repositories.ticket_repository import TicketRepository

_ALLOWED_STATUS_TRANSITIONS = {
    "created": {"in_progress", "cancelled"},
    "in_progress": {"resolved", "cancelled"},
    "resolved": {"closed", "in_progress"},
    "closed": set(),
    "cancelled": set(),
}

class TicketService:
    def __init__(self, repository: TicketRepository | None = None) -> None:
        self.repository = repository or TicketRepository()

    def create_approved_ticket(
        self,
        session: Session,
        *,
        title: str,
        description: str,
        category: str,
        priority: str,
        created_by: str,
        approved_by: str,
    ) -> Ticket:
        ticket = Ticket(
            ticket_number=self._generate_ticket_number(),
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="created",
            created_by=created_by,
            approved_by=approved_by,
        )

        ticket = self.repository.create_ticket(session, ticket)

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="ticket_created",
            old_status=None,
            new_status="created",
            performed_by=approved_by,
            details={
                "source": "internal_ticket_service",
            },
        )

        self.repository.add_event(session, event)

        return ticket

    @staticmethod
    def _generate_ticket_number() -> str:
        return f"SUP-{uuid4().hex[:10].upper()}"

    def get_ticket(
    self,
    session: Session,
    ticket_id: int,
    ) -> Ticket | None:
        return self.repository.get_ticket_by_id(
            session,
            ticket_id,
        )

    def update_ticket_status(
    self,
    session: Session,
    *,
    ticket_id: int,
    new_status: str,
    performed_by: str,
    ) -> Ticket:
        ticket = self.repository.get_ticket_by_id(
            session,
            ticket_id,
        )

        if ticket is None:
            raise LookupError("Ticket not found.")

        allowed_statuses = _ALLOWED_STATUS_TRANSITIONS.get(
            ticket.status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise ValueError(
                f"Cannot change ticket from "
                f"'{ticket.status}' to '{new_status}'."
            )

        old_status = ticket.status

        self.repository.update_status(
            session,
            ticket,
            new_status,
        )

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="status_changed",
            old_status=old_status,
            new_status=new_status,
            performed_by=performed_by,
            details=None,
        )

        self.repository.add_event(
            session,
            event,
        )

        return ticket

    def create_ticket_draft(
    self,
    session: Session,
    *,
    title: str,
    description: str,
    category: str,
    priority: str,
    created_by: str,
    ) -> Ticket:
        ticket = Ticket(
            ticket_number=self._generate_ticket_number(),
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="pending_approval",
            created_by=created_by,
            approved_by=None,
        )

        ticket = self.repository.create_ticket(session, ticket)

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="ticket_draft_created",
            old_status=None,
            new_status="pending_approval",
            performed_by=created_by,
            details={
                "source": "internal_ticket_service",
            },
        )

        self.repository.add_event(session, event)

        return ticket

    def approve_ticket(
    self,
    session: Session,
    *,
    ticket_id: int,
    approved_by: str,
    ) -> Ticket:
        ticket = self.repository.get_ticket_by_id(
            session,
            ticket_id,
        )

        if ticket is None:
            raise LookupError("Ticket not found.")

        if ticket.status != "pending_approval":
            raise ValueError(
                "Only pending tickets can be approved."
            )

        old_status = ticket.status
        ticket.approved_by = approved_by

        self.repository.update_status(
            session,
            ticket,
            "created",
        )

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="ticket_approved",
            old_status=old_status,
            new_status="created",
            performed_by=approved_by,
            details=None,
        )

        self.repository.add_event(session, event)

        return ticket

    def list_tickets(
    self,
    session: Session,
    *,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    ) -> list[Ticket]:
        return self.repository.list_tickets(
            session,
            status=status,
            limit=limit,
            offset=offset,
        )
