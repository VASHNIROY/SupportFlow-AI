from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketEvent


class TicketRepository:
    def create_ticket(
        self,
        session: Session,
        ticket: Ticket,
    ) -> Ticket:
        session.add(ticket)
        session.flush()
        return ticket

    def get_ticket_by_id(
        self,
        session: Session,
        ticket_id: int,
    ) -> Ticket | None:
        statement = select(Ticket).where(Ticket.id == ticket_id)
        return session.scalar(statement)

    def add_event(
        self,
        session: Session,
        event: TicketEvent,
    ) -> TicketEvent:
        session.add(event)
        session.flush()
        return event

    def update_status(
        self,
        session: Session,
        ticket: Ticket,
        new_status: str,
    ) -> Ticket:
        ticket.status = new_status
        session.add(ticket)
        session.flush()
        return ticket

    def list_tickets(
    self,
    session: Session,
    *,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    ) -> list[Ticket]:
        statement = select(Ticket)

        if status is not None:
            statement = statement.where(
                Ticket.status == status,
            )

        statement = (
            statement
            .order_by(Ticket.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(session.scalars(statement).all())
