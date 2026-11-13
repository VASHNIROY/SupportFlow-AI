from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    ticket_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="medium",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="pending_approval",
    )

    created_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    approved_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    external_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    external_ticket_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    events: Mapped[list["TicketEvent"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class TicketEvent(Base):
    __tablename__ = "ticket_events"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    new_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    performed_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    ticket: Mapped["Ticket"] = relationship(
        back_populates="events",
    )
