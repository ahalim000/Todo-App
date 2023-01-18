from typing import Any, Dict, List, Optional, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session
from todo.backend.storage.models import OwnerIdMixin, User

from sqlalchemy import inspect

OwnerIdGeneric = TypeVar("OwnerIdGeneric", bound=OwnerIdMixin)


class StorageManager:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def list(
        self,
        model_cls: Type[OwnerIdGeneric],
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[Any]] = None,
    ) -> OwnerIdGeneric:
        query = self.db.query(model_cls)

        if self.user.role == "user":
            query = query.filter_by(owner_id=self.user.owner_id)

        if filters:
            query = query.filter_by(**filters)

        if order_by:
            query = query.order_by(*order_by)

        return query.all()

    def create(self, model_cls: Type[OwnerIdGeneric], data: Dict[str, Any]) -> OwnerIdGeneric:
        data = data.copy()
        if "owner_id" in inspect(model_cls).columns:
            data["owner_id"] = self.user.id

        item = model_cls(**data)

        self.db.add(item)
        self.db.flush()

        return item

    def get(self, model_cls: Type[OwnerIdGeneric], filters: Dict[str, Any]) -> OwnerIdGeneric:
        query = self.db.query(model_cls).filter_by(**filters)

        if self.user.role == "user":
            query = query.filter_by(owner_id=self.user.owner_id)

        item = query.one_or_none()

        if item is None:
            raise HTTPException(400, detail=f"{model_cls.__name__} doesn't exist")

        return item

    def update(self, model_cls: Type[OwnerIdGeneric], filters: Dict[str, Any], data: Dict[str, Any]) -> OwnerIdGeneric:
        query = self.db.query(model_cls).filter_by(**filters)

        if self.user.role == "user":
            query = query.filter_by(owner_id=self.user.owner_id)

        item = query.one_or_none()

        if item is None:
            raise HTTPException(400, detail=f"{model_cls.__name__} doesn't exist")

        for key, val in data.items():
            setattr(item, key, val)

        self.db.add(item)
        self.db.flush()

        return item

    def delete(self, model_cls: Type[OwnerIdGeneric], filters: Dict[str, Any]) -> OwnerIdGeneric:
        query = self.db.query(model_cls).filter_by(**filters)

        if self.user.role == "user":
            query = query.filter_by(owner_id=self.user.owner_id)

        item = query.one_or_none()

        if item is None:
            raise HTTPException(400, detail=f"{model_cls.__name__} doesn't exist")

        self.db.delete(item)
        self.db.flush()

        return item
