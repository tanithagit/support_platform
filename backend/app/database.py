from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    # Import all models so SQLModel registers them
    from app.models import (
        Organization, User, Ticket, Message, ActivityLog
    )
    SQLModel.metadata.create_all(engine)