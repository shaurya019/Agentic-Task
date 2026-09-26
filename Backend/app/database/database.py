"""
database.py — Database connection (engine), session factory, and Base class.

- engine:        knows HOW to talk to SQLite (the file tasks.db)
- SessionLocal:  creates a "unit of work" (Session) per request
- Base:          parent class for our ORM models
- get_db():      FastAPI dependency that opens a session and always closes it
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# check_same_thread=False: FastAPI may use the session from a different thread
# than the one that created it. Needed for SQLite only.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Create tables if they don't exist (fine for learning; use Alembic in production)."""
    from app.models import task  # noqa: F401  (import registers the model with Base)

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
