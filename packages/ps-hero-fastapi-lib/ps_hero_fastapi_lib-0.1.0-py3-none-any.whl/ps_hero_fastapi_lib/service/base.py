from typing import Generic, TypeVar, List, Any, Optional
from sqlmodel import Session, SQLModel
from repository.base import Repository, ModelT, CreateT, UpdateT

class Service(Generic[ModelT, CreateT, UpdateT]):
    def __init__(self, repo: Repository[ModelT, CreateT, UpdateT]):
        self.repo = repo
    # fim_def

    def get(self, session: Session, id: Any) -> Optional[ModelT]:
        return self.repo.get(session, id)
    # fim_def

    def list(self, session: Session, offset: int = 0, limit: int = 100) -> List[ModelT]:
        return self.repo.list(session, offset, limit)
    # fim_def

    def create(self, session: Session, data: CreateT) -> ModelT:
        return self.repo.create(session, data)
    # fim_def

    def update(self, session: Session, id: Any, data: UpdateT) -> ModelT:
        obj = self.repo.get(session, id)
        if not obj:
            raise ValueError("Not found")
        return self.repo.update(session, obj, data)
    # fim_def

    def delete(self, session: Session, id: Any) -> None:
        obj = self.repo.get(session, id)
        if not obj:
            raise ValueError("Not found")
        return self.repo.delete(session, obj)
    # fim_def
# fim_class
