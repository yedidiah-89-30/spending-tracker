from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Thin generic CRUD wrapper. Repositories exist to isolate every raw
    SQLAlchemy query behind a plain method call, so services never import
    `Session`/ORM models directly and can be tested with a fake repository
    instead of a real database."""

    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id_: int) -> ModelType | None:
        return self.db.get(self.model, id_)

    def add(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.commit()
