import os, secrets
import pytest

from datetime import datetime, timedelta
from functools import wraps
from fastapi.testclient import TestClient

os.environ["TODO_DATABASE_URL"] = "postgresql:///test_todo"
os.environ["TODO_SECRET_KEY"] = secrets.token_hex(32)

from todo.backend.storage.database import SessionLocal, Base, engine
from todo.backend.routes.users import hash_password, create_oauth_token
from todo.backend.storage import models  # Exectuted for side effect
from todo.backend.app import init_app
from todo.backend.dependencies import get_db

DB_SEEDED = False

app = init_app()
client = TestClient(app)


def get_token(username):
    return create_oauth_token({"sub": username, "exp": datetime.utcnow() + timedelta(minutes=60)})


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
        db.commit()

        todo_1 = models.Todo(name="Todo 1", owner_id=user_1.id)
        for i in range(10):
            todo_1.todo_items.append(models.TodoItem(message=f"Paper Crane {i + 1}", position=chr(i + 97)))

        todo_2 = models.Todo(name="Todo 2", owner_id=user_2.id)
        for i in range(10):
            todo_2.todo_items.append(models.TodoItem(message=f"Paper Boats {i + 2}", position=chr(i + 97)))

        db.add_all([todo_1, todo_2])
        db.commit()
        DB_SEEDED = True

    def new_save_point_commit(original_func):
        def wrapper():
            db.begin_nested()
            original_func()

        return wrapper

    db.commit = new_save_point_commit(db.commit)
    app.dependency_overrides[get_db] = lambda: db

    savepoint = db.begin_nested()
    yield db
    savepoint.rollback()
    db.close()


def test_authentication():
    # Try without auth
    user_response = client.get("/api/users/me")
    assert user_response.status_code == 401
    # Get Token
    token_request = client.post(
        "/api/token",
        data="username=admin&password=admin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_request.status_code == 200
    token_request_data = token_request.json()
    token = token_request_data["access_token"]
    # Try with auth
    user_response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert user_response.status_code == 200
    user_response_data = user_response.json()
    assert user_response_data["username"] == "admin"
    assert user_response_data["role"] == "admin"


def test_list_todo():
    # Test admin access
    admin_token = get_token("admin")
    response = client.get("/api/todos", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    todo_1, todo_2 = tuple(sorted(data["items"], key=lambda x: x["name"]))
    assert {"name": "Todo 1"}.items() <= todo_1.items()
    assert {"name": "Todo 2"}.items() <= todo_2.items()

    user_1_token = get_token("user1")
    response = client.get("/api/todos", headers={"Authorization": f"Bearer {user_1_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_create_todo(db):
    # user_1 = db.query(models.User).filter_by(username="user1").one()
    # user_1_token = get_token("user1")
    # response = client.post("/api/todos", headers={"Authorization": f"Bearer {user_1_token}"}, json={"name": "Todo 3"})
    # assert response.status_code == 200
    # data = response.json()
    # assert data["name"] == "Todo 3"
    # assert data["owner_id"] == user_1.owner_id
    # assert len(db.query(models.Todo).filter_by(owner_id=user_1.id).all()) == 2
    # for i in range(10):
    #     response = client.post(
    #         "/api/todos", headers={"Authorization": f"Bearer {user_1_token}"}, json={"name": "Todo 3"}
    #     )
    #     assert len(db.query(models.Todo).filter_by(owner_id=user_1.id).all()) == 3 + i

    user_3 = models.User(username="user3", hashed_password=hash_password("user2"), role="user")
    db.add(user_3)
    db.commit()
    user_4 = models.User(username="user4", hashed_password=hash_password("user2"), role="user")
    db.add(user_4)
    db.commit()
    print(user_4.owner_id)
