from typing import Generic, TypeVar, Type, Optional
from sqlmodel import SQLModel, Session, select

ModelT = TypeVar("ModelT", bound=SQLModel)
CreateT = TypeVar("CreateT", bound=SQLModel)
UpdateT = TypeVar("UpdateT", bound=SQLModel)


class Repository(Generic[ModelT, CreateT, UpdateT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    def create(self, session: Session, obj_in: CreateT) -> ModelT:
        data = obj_in.dict(exclude_unset=True)
        obj = self.model(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def list(self, session: Session, offset: int = 0, limit: int = 100) -> list[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        return session.exec(statement).all()

    def get(self, session: Session, id: int) -> Optional[ModelT]:
        return session.get(self.model, id)

    def update(self, session: Session, id: int, obj_in: UpdateT) -> ModelT:
        obj = self.get(session, id)
        if not obj:
            raise ValueError("Not found")
        data = obj_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(obj, key, value)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, id: int) -> None:
        obj = self.get(session, id)
        if not obj:
            raise ValueError("Not found")
        session.delete(obj)
        session.commit()


class Service(Generic[ModelT, CreateT, UpdateT]):
    def __init__(self, repo: Repository[ModelT, CreateT, UpdateT]):
        self.repo = repo

    def create(self, session: Session, payload: CreateT) -> ModelT:
        return self.repo.create(session, payload)

    def list(self, session: Session, offset: int, limit: int) -> list[ModelT]:
        return self.repo.list(session, offset, limit)

    def get(self, session: Session, id: int) -> Optional[ModelT]:
        return self.repo.get(session, id)

    def update(self, session: Session, id: int, payload: UpdateT) -> ModelT:
        return self.repo.update(session, id, payload)

    def delete(self, session: Session, id: int) -> None:
        return self.repo.delete(session, id)
