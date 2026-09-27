"""Async SQLAlchemy persistence for clinical stream metadata."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _database_url(value: str) -> str:
    value = value.strip()
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+asyncpg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+asyncpg://", 1)
    if value.startswith("sqlite://"):
        return value.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return value


def get_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL", "").strip()
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_ENVIRONMENT_NAME")
    if not configured_url and is_railway:
        raise RuntimeError("DATABASE_URL is required in Railway environments")
    return _database_url(configured_url or "sqlite+aiosqlite:///./edge_sync.sqlite3")


DATABASE_URL = get_database_url()


class Base(DeclarativeBase):
    pass


class ClinicSession(Base):
    __tablename__ = "clinic_sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    clinic_id: Mapped[str] = mapped_column(String, nullable=False)
    language_code: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_transcript: Mapped[str] = mapped_column(Text, nullable=False, default="")


class TranscriptEvent(Base):
    __tablename__ = "transcript_events"
    __table_args__ = (Index("idx_transcript_events_session", "session_id", "created_at"),)

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("clinic_sessions.session_id"), nullable=False
    )
    clinic_id: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EdgePersistence:
    """Persist stream transcripts without storing raw audio."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = _database_url(database_url or DATABASE_URL)
        self.backend = "postgresql" if self.database_url.startswith("postgresql+") else "sqlite"
        options = {"pool_pre_ping": True}
        if self.backend == "postgresql":
            options.update(pool_size=5, max_overflow=5)
        self.engine = create_async_engine(self.database_url, **options)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def initialize(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    async def start_session(self, *, clinic_id: str, language_code: str) -> str:
        session_id = str(uuid.uuid4())
        async with self.session_factory.begin() as session:
            session.add(
                ClinicSession(
                    session_id=session_id,
                    clinic_id=clinic_id,
                    language_code=language_code,
                    started_at=utc_now(),
                )
            )
        return session_id

    async def record_transcript(
        self,
        *,
        session_id: str,
        clinic_id: str,
        transcript: str,
        event_type: str,
    ) -> None:
        created_at = utc_now()
        async with self.session_factory.begin() as session:
            session.add(
                TranscriptEvent(
                    event_id=str(uuid.uuid4()),
                    session_id=session_id,
                    clinic_id=clinic_id,
                    event_type=event_type,
                    transcript=transcript,
                    created_at=created_at,
                )
            )
            await session.execute(
                update(ClinicSession)
                .where(ClinicSession.session_id == session_id)
                .values(
                    last_transcript=transcript,
                    ended_at=created_at if event_type == "final" else ClinicSession.ended_at,
                )
            )


persistence = EdgePersistence()