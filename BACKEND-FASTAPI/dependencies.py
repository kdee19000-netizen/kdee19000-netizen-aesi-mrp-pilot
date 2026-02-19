"""Database session dependency for FastAPI route handlers."""

from models.base import SessionLocal


def get_db():
    """Yield a SQLAlchemy database session, closing it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
