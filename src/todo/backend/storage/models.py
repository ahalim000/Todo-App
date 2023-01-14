from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declared_attr, declarative_mixin, synonym
from sqlalchemy.ext.associationproxy import association_proxy

from todo.backend.ranking import get_lexical_rank
from todo.backend.storage.database import Base


@declarative_mixin
class OwnerIdMixin:
    @declared_attr
    def owner_id(cls):
        return Column(Integer, ForeignKey("user.id"))


class User(OwnerIdMixin, Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    @declared_attr
    def owner_id(cls):
        return synonym("id")


class Todo(OwnerIdMixin, Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    todo_items = relationship(
        "TodoItem", back_populates="todo", cascade="all, delete-orphan", order_by="TodoItem.position"
    )

    def rerank_todo_items(self):
        self.todo_items[0].position = "b"
        self.todo_items[-1].position = "z"

        self._rerank_todo_items(0, len(self.todo_items) - 1)

    def _rerank_todo_items(self, start_idx, end_idx):
        if end_idx - start_idx <= 1:
            return

        mid_idx = (start_idx + end_idx) // 2
        mid_ti = self.todo_items[mid_idx]
        mid_ti.position = get_lexical_rank(self.todo_items[start_idx].position, self.todo_items[end_idx].position)

        self._rerank_todo_items(start_idx, mid_idx)
        self._rerank_todo_items(mid_idx, end_idx)


class TodoItem(OwnerIdMixin, Base):
    __tablename__ = "todo_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    position = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    todo_id = Column(Integer, ForeignKey(Todo.id))
    todo = relationship("Todo", back_populates="todo_items")

    @declared_attr
    def owner_id(cls):
        return association_proxy("todo", "owner_id")
