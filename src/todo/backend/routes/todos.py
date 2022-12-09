from fastapi import APIRouter, Depends
from todo.backend.dependencies import get_db
from todo.backend.storage.database import SessionLocal
from todo.backend.storage.models import Todo, TodoItem
from todo.backend.ranking import get_lexical_rank
from pydantic import BaseModel


class TodoCreateUpdateSchema(BaseModel):
    name: str


class TodoReorderSchema(BaseModel):
    todo_item_id: int
    insert_idx: int


router = APIRouter(prefix="/api/todos")


@router.get("/")
def list_todos(db: SessionLocal = Depends(get_db)):
    todos = []
    for todo in db.query(Todo):
        todos.append(todo.to_dict())

    return {"items": todos}


@router.post("/")
def create_todo(request_data: TodoCreateUpdateSchema, db: SessionLocal = Depends(get_db)):
    todo = Todo(name=request_data.name)
    db.add(todo)
    # INSERT INTO todo (name) VALUES ('First Todo') RETURNING todo.id
    db.commit()
    # SELECT todo_item.id AS todo_item_id, todo_item.message AS todo_item_message, todo_item.todo_id AS todo_item_todo_id, todo_item.position AS todo_item_position
    # FROM todo_item
    # WHERE todo_item.todo_id = 1
    # ORDER BY todo_item.position
    return todo.to_dict()


@router.get("/{id}")
def get_todo(id: int, db: SessionLocal = Depends(get_db)):
    todo = db.query(Todo).filter_by(id=id).one()

    return todo.to_dict()


@router.put("/{id}")
def update_todo(id: int, request_data: TodoCreateUpdateSchema, db: SessionLocal = Depends(get_db)):
    todo = db.query(Todo).filter_by(id=id).one()
    todo.name = request_data.name
    db.add(todo)
    db.commit()

    return todo.to_dict()


@router.delete("/{id}")
def delete_todo(id: int, db: SessionLocal = Depends(get_db)):
    todo = db.query(Todo).filter_by(id=id).one()
    db.delete(todo)
    db.commit()

    return todo.to_dict()


@router.put("/{id}/reorder", status_code=201)
def reorder_todo(id: int, request_data: TodoReorderSchema, db: SessionLocal = Depends(get_db)):
    todo: Todo = db.query(Todo).filter_by(id=id).one()
    todo_item_id = request_data.todo_item_id
    insert_idx = request_data.insert_idx

    if insert_idx < 0:
        insert_idx = 0
    if insert_idx >= len(todo.todo_items):
        insert_idx = len(todo.todo_items) - 1

    todo_item: TodoItem = db.query(TodoItem).filter_by(id=todo_item_id).filter_by(todo_id=id).one()
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
    db.commit()
