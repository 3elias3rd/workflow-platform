from typing import Generator
from app.db.database import SessionLocal
from sqlalchemy.orm import Session

def get_db() -> Generator:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
