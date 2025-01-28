from functools import wraps
from typing import Callable, TypeVar, Any
from contextlib import contextmanager

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

T = TypeVar("T")


@contextmanager
def transaction_context(db: Session):
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def transactional(func: Callable[..., T]) -> Callable[..., T]:

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        db = next((arg for arg in args if isinstance(arg, Session)), kwargs.get('db'))
        if not db:
            raise ValueError("Database session not found in arguments")

        with transaction_context(db):
            return func(*args, **kwargs)

    return wrapper


class BaseRepository:

    def __init__(self, db: Session):
        self.db = db

    @contextmanager
    def transaction(self):
        with transaction_context(self.db) as session:
            yield session

    def save(self, obj):
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.flush()

    def refresh(self, obj):
        self.db.refresh(obj)
        return obj