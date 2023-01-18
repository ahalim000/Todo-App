from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from todo.backend.dependencies import get_db, get_current_user, get_storage_manager
from todo.backend.storage.models import Todo, TodoItem
from todo.backend.ranking import get_lexical_rank
from pydantic import BaseModel

from todo.backend.storage.storage_manager import StorageManager

MAX_RANK_LENGTH = 128


class TodoItemCreateSchema(BaseModel):
    todo_id: int
    message: str


class TodoItemUpdateSchema(BaseModel):
    message: str


class TodoItemSchema(BaseModel):
    id: int
    message: str
    active: bool
    todo_id: int
    owner_id: int

    class Config:
        orm_mode = True


class ListTodoItemSchema(BaseModel):
    items: List[TodoItemSchema]


router = APIRouter(
    prefix="/api/todoitems",
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=ListTodoItemSchema)
def list_todo_items(todo_id: Optional[int] = None, sm: StorageManager = Depends(get_storage_manager)):
    filters = {}
    if todo_id is not None:
        filters["todo_id"] = todo_id

    todo_items = sm.list(TodoItem, filters, [TodoItem.todo_id, TodoItem.position])
    return {"items": todo_items}


@router.post("", response_model=TodoItemSchema)
def create_todo_items(
    request_data: TodoItemCreateSchema, sm: StorageManager = Depends(get_storage_manager), db: Session = Depends(get_db)
):
    todo = sm.get(Todo, {"id": request_data.todo_id})
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
    db.flush()

    if needs_reorder:
        db.refresh(todo)
        todo.rerank_todo_items()
        db.add(todo)
        db.flush()

    return todo_item


@router.get("/{id}", response_model=TodoItemSchema)
def get_todo_item(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.get(TodoItem, {"id": id})


@router.put("/{id}", response_model=TodoItemSchema)
def update_todo_item(id: int, request_data: TodoItemUpdateSchema, sm: StorageManager = Depends(get_storage_manager)):
    return sm.update(TodoItem, {"id": id}, request_data.dict())


@router.delete("/{id}", response_model=TodoItemSchema)
def delete_todo_item(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.delete(TodoItem, {"id": id})


@router.put("/{id}/toggle", response_model=TodoItemSchema)
def toggle_todo_item(id: int, sm: StorageManager = Depends(get_storage_manager), db: Session = Depends(get_db)):
    todo_item = sm.get(TodoItem, {"id": id})
    todo_item.active = not todo_item.active

    db.add(todo_item)
    db.flush()

    return todo_item
