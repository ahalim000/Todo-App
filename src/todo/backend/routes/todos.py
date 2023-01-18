from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from todo.backend.dependencies import get_db, get_current_user, get_storage_manager
from sqlalchemy.orm import Session
from todo.backend.storage.models import Todo, TodoItem, User
from todo.backend.storage.storage_manager import StorageManager
from todo.backend.ranking import get_lexical_rank
from pydantic import BaseModel


class TodoCreateUpdateSchema(BaseModel):
    name: str


class TodoReorderSchema(BaseModel):
    todo_item_id: int
    insert_idx: int


class TodoSchema(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        orm_mode = True


class ListTodoSchema(BaseModel):
    items: List[TodoSchema]


router = APIRouter(
    prefix="/api/todos",
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=ListTodoSchema)
def list_todos(sm: StorageManager = Depends(get_storage_manager)):
    todos = sm.list(Todo)
    return {"items": todos}


@router.post("", response_model=TodoSchema)
def create_todo(request_data: TodoCreateUpdateSchema, sm: StorageManager = Depends(get_storage_manager)):
    # On request (No ORM Mode):
    # JSON (str) -> dict -> TodoCreateUpdateSchema.from_obj(dict) -> TodoCreateUpdateSchema instance (request_data)

    # dict['name']
    # dict['todo_id']

    # On response (ORM Mode):
    # Todo instance (inst) -> TodoSchema.from_orm(inst) -> dict -> JSON (str)

    # getattr(inst, 'name')
    # getattr(inst, 'todo_id')

    return sm.create(Todo, request_data.dict())


@router.get("/{id}", response_model=TodoSchema)
def get_todo(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.get(Todo, {"id": id})


@router.put("/{id}", response_model=TodoSchema)
def update_todo(id: int, request_data: TodoCreateUpdateSchema, sm: StorageManager = Depends(get_storage_manager)):
    return sm.update(Todo, {"id": id}, request_data.dict())


@router.delete("/{id}", response_model=TodoSchema)
def delete_todo(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.delete(Todo, {"id": id})


@router.put("/{id}/reorder", status_code=204)
def reorder_todo(
    id: int,
    request_data: TodoReorderSchema,
    sm: StorageManager = Depends(get_storage_manager),
    db: Session = Depends(get_db),
):
    todo = sm.get(Todo, {"id": id})

    todo_item_id = request_data.todo_item_id
    insert_idx = request_data.insert_idx

    if insert_idx < 0:
        insert_idx = 0
    if insert_idx >= len(todo.todo_items):
        insert_idx = len(todo.todo_items) - 1

    todo_item = sm.get(TodoItem, {"id": todo_item_id, "todo_id": id})
    todo_idx = todo.todo_items.index(todo_item)

    todo.todo_items.pop(todo_idx)
    todo.todo_items.insert(insert_idx, todo_item)
    if len(todo.todo_items) == 1:
        return

    if len(todo.todo_items) == 2:
        todo.todo_items[0].position = "b"
        todo.todo_items[1].position = "z"
    elif insert_idx == 0:
        todo_item.position = "b"
        todo.todo_items[1].position = get_lexical_rank(todo.todo_items[0].position, todo.todo_items[2].position)
    elif insert_idx == len(todo.todo_items) - 1:
        todo_item.position = "z"
        todo.todo_items[-2].position = get_lexical_rank(todo.todo_items[-3].position, todo.todo_items[-1].position)
    else:
        todo_item.position = get_lexical_rank(
            todo.todo_items[insert_idx - 1].position, todo.todo_items[insert_idx + 1].position
        )

    db.add(todo)
    db.flush()

    return Response(status_code=204)
