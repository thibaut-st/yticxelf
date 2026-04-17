from pathlib import Path

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent / "flexcity.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


class Base(DeclarativeBase):
    """Declarative base shared by the application's ORM models."""

    metadata = MetaData()


def make_engine(database_url: str = DATABASE_URL) -> Engine:
    """Create an SQLAlchemy engine for the configured SQLite database."""
    return create_engine(database_url)


def make_session_factory(db_engine: Engine | None = None) -> sessionmaker[Session]:
    """Create a session factory bound to the provided engine."""
    bound_engine = db_engine if db_engine is not None else make_engine()
    # expire_on_commit=False: objects keep their loaded values after commit.
    return sessionmaker(bind=bound_engine, autoflush=False, expire_on_commit=False)


engine = make_engine()
SessionLocal = make_session_factory(engine)
