import os, secrets
import pytest

os.environ["TODO_DATABASE_URL"] = "postgresql:///test_todo"
os.environ["TODO_SECRET_KEY"] = secrets.token_hex(32)

from todo.backend.storage import models  # Exectuted for side effect
from todo.backend.storage.database import SessionLocal, Base, engine
from todo.backend.routes.users import hash_password
from todo.backend.storage import models
from todo.backend.dependencies import get_db
from todo.backend.app import init_app
from fastapi.testclient import TestClient

DB_SEEDED = False

app = init_app()
client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def db():
    global DB_SEEDED

    db = SessionLocal()
    if not DB_SEEDED:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        admin = models.User(username="admin", hashed_password=hash_password("admin"), role="admin")
        user_1 = models.User(username="user1", hashed_password=hash_password("user1"), role="user")
        user_2 = models.User(username="user2", hashed_password=hash_password("user2"), role="user")
        db.add_all([admin, user_1, user_2])
        db.flush()

        todo_1 = models.Todo(name="Todo 1", owner_id=user_1.id)
        for i in range(10):
            todo_1.todo_items.append(models.TodoItem(message=f"Paper Crane {i + 1}", position=chr(i + 97)))

        todo_2 = models.Todo(name="Todo 2", owner_id=user_2.id)
        for i in range(10):
            todo_2.todo_items.append(models.TodoItem(message=f"Paper Boat {i + 1}", position=chr(i + 97)))

        db.add_all([todo_1, todo_2])
        db.commit()
        DB_SEEDED = True

    app.dependency_overrides[get_db] = lambda: db

    savepoint = db.begin_nested()
    yield db
    savepoint.rollback()
    db.close()
