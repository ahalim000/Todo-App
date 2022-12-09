from fastapi import APIRouter, Depends
from todo.backend.dependencies import get_db
from todo.backend.storage.database import SessionLocal
from todo.backend.storage.models import Todo, TodoItem
from todo.backend.ranking import get_lexical_rank
from pydantic import BaseModel

MAX_RANK_LENGTH = 128


class TodoItemCreateSchema(BaseModel):
    todo_id: int
    message: str


class TodoItemUpdateSchema(BaseModel):
    message: str


router = APIRouter(prefix="/api/todoitems")


@router.get("/")
def list_todo_items(db: SessionLocal = Depends(get_db)):
    todo_items = []
    for todo_item in db.query(TodoItem):
        todo_items.append(todo_item.to_dict())

    return {"items": todo_items}


@router.post("/")
def create_todo_items(request_data: TodoItemCreateSchema, db: SessionLocal = Depends(get_db)):
    todo = db.query(Todo).filter_by(id=request_data.todo_id).one()
    todo_item = TodoItem(todo_id=request_data.todo_id, message=request_data.message)

    needs_reorder = False
    if len(todo.todo_items) == 0:
        todo_item.position = "b"
    elif len(todo.todo_items) == 1:
        todo_item.position = "z"
    else:
        todo_item.position = "z"

        prev_last = todo.todo_items[-1]
        prev_penultimate = todo.todo_items[-2]
        new_lex_rank = get_lexical_rank(prev_penultimate.position, todo_item.position)
        if len(new_lex_rank) > MAX_RANK_LENGTH:
            needs_reorder = True
        prev_last.position = new_lex_rank
        db.add(prev_last)

    db.add(todo_item)
    db.commit()

    if needs_reorder:
        db.refresh(todo)
        todo.rerank_todo_items()
        db.add(todo)
        db.commit()

    return todo_item.to_dict()


@router.get("/{id}")
def get_todo_item(id: int, db: SessionLocal = Depends(get_db)):
    todo_item = db.query(TodoItem).filter_by(id=id).one()

    return todo_item.to_dict()


@router.put("/{id}")
def update_todo_item(id: int, request_data: TodoItemUpdateSchema, db: SessionLocal = Depends(get_db)):
    todo_item = db.query(TodoItem).filter_by(id=id).one()
    todo_item.message = request_data.message
    db.add(todo_item)
    db.commit()

    return todo_item.to_dict()


@router.delete("/{id}")
def delete_todo_item(id: int, db: SessionLocal = Depends(get_db)):
    todo_item = db.query(TodoItem).filter_by(id=id).one()
    db.delete(todo_item)
    db.commit()

    return todo_item.to_dict()


@router.put("/{id}/toggle")
def toggle_todo_item(id: int, db: SessionLocal = Depends(get_db)):
    todo_item = db.query(TodoItem).filter_by(id=id).one()
    todo_item.active = not todo_item.active
    db.add(todo_item)
    db.commit()

    return todo_item.to_dict()
