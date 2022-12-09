from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from todo.backend.ranking import get_lexical_rank
from todo.backend.storage.database import Base


class Todo(Base):
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

    def to_dict(self):
        todo_items = [todo_item.to_dict() for todo_item in self.todo_items]
        for idx, todo_item in enumerate(todo_items):
            todo_item["index"] = idx

        res = {"id": self.id, "name": self.name, "todo_items": todo_items}

        return res


class TodoItem(Base):
    __tablename__ = "todo_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    todo_id = Column(Integer, ForeignKey(Todo.id))
    position = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    todo = relationship("Todo", back_populates="todo_items")

    def to_dict(self):
        res = {
            "id": self.id,
            "message": self.message,
            "todo_id": self.todo_id,
            "active": self.active,
            "position": self.position,
        }

        return res
