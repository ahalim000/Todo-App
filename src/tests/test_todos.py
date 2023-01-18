from tests.conftest import client
from tests.utils import get_token
from todo.backend.storage import models


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
    user_1 = db.query(models.User).filter_by(username="user1").one()
    user_1_token = get_token("user1")
    response = client.post("/api/todos", headers={"Authorization": f"Bearer {user_1_token}"}, json={"name": "Todo 3"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Todo 3"
    assert data["owner_id"] == user_1.id
    assert len(db.query(models.Todo).filter_by(owner_id=user_1.id).all()) == 2
    for i in range(10):
        response = client.post(
            "/api/todos", headers={"Authorization": f"Bearer {user_1_token}"}, json={"name": f"Todo {3 + i}"}
        )
        assert len(db.query(models.Todo).filter_by(owner_id=user_1.id).all()) == 2 + (i + 1)


def test_get_todo():
    id = 1
    admin_token = get_token("admin")
    response = client.get(f"/api/todos/{id}", headers={"Authorization": f"Bearer {admin_token}"}, params={"id": id})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id

    user_1_token = get_token("user1")
    response = client.get(f"/api/todos/{id}", headers={"Authorization": f"Bearer {user_1_token}"}, params={"id": id})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id

    user_2_token = get_token("user2")
    response = client.get(f"/api/todos/{id}", headers={"Authorization": f"Bearer {user_2_token}"}, params={"id": id})
    assert response.status_code == 400


def test_update_todo():
    id = 1
    admin_token = get_token("admin")
    response = client.put(
        f"/api/todos/{id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"id": id},
        json={"name": "Test Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Name"

    user_1_token = get_token("user1")
    response = client.put(
        f"/api/todos/{id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        params={"id": id},
        json={"name": "Test Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Name"

    user_2_token = get_token("user2")
    response = client.put(
        f"/api/todos/{id}",
        headers={"Authorization": f"Bearer {user_2_token}"},
        params={"id": id},
        json={"name": "Test Name"},
    )
    assert response.status_code == 400


def test_delete_todo(db):
    id = 1
    admin_token = get_token("admin")
    todo = db.query(models.Todo).filter_by(id=id).one()
    response = client.delete(f"/api/todos/{id}", headers={"Authorization": f"Bearer {admin_token}"}, params={"id": id})
    assert response.status_code == 200
    todos = db.query(models.Todo).all()
    assert todo not in todos

    id = 2
    user_1_token = get_token("user1")
    response = client.delete(f"/api/todos/{id}", headers={"Authorization": f"Bearer {user_1_token}"}, params={"id": id})
    assert response.status_code == 400

    user_2_token = get_token("user2")
    todo = db.query(models.Todo).filter_by(id=id).one()
    response = client.delete(f"/api/todos/{id}", headers={"Authorization": f"Bearer {user_2_token}"}, params={"id": id})
    assert response.status_code == 200
    todos = db.query(models.Todo).all()
    assert todo not in todos


def test_reorder_todo(db):
    id = 1
    admin_token = get_token("admin")
    todo = db.query(models.Todo).filter_by(id=id).one()
    todo_item = todo.todo_items[4]
    response = client.put(
        f"/api/todos/{id}/reorder",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"id": id},
        json={"todo_item_id": todo_item.id, "insert_idx": 7},
    )
    assert response.status_code == 204
    assert todo.todo_items[7] == todo_item

    user_1_token = get_token("user1")
    todo = db.query(models.Todo).filter_by(id=id).one()
    todo_item = todo.todo_items[0]
    for idx in [9, 0, 3, 3, 20, -3]:
        if idx < 0:
            idx = 0
        if idx >= len(todo.todo_items):
            idx = len(todo.todo_items) - 1
        response = client.put(
            f"/api/todos/{id}/reorder",
            headers={"Authorization": f"Bearer {user_1_token}"},
            params={"id": id},
            json={"todo_item_id": todo_item.id, "insert_idx": idx},
        )
        assert response.status_code == 204
        assert todo.todo_items[idx] == todo_item

    user_2_token = get_token("user2")
    todo = db.query(models.Todo).filter_by(id=id).one()
    todo_item = todo.todo_items[4]
    response = client.put(
        f"/api/todos/{id}/reorder",
        headers={"Authorization": f"Bearer {user_2_token}"},
        params={"id": id},
        json={"todo_item_id": todo_item.id, "insert_idx": 7},
    )
    assert response.status_code == 400
