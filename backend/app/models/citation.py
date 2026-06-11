import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class CitationStyle(str, enum.Enum):
    APA = "apa"
    MLA = "mla"
    HARVARD = "harvard"
    CHICAGO = "chicago"
    IEEE = "ieee"


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    style: Mapped[CitationStyle] = mapped_column(SAEnum(CitationStyle), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[int | None] = mapped_column(nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    journal: Mapped[str | None] = mapped_column(String(500), nullable=True)
    volume: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issue: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pages: Mapped[str | None] = mapped_column(String(50), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    accessed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)
    extra_data: Mapped[dict | None] = mapped_column("meta", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="citations")
