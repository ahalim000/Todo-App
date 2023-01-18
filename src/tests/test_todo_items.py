from tests.conftest import client
from tests.utils import get_token
from todo.backend.storage import models


def test_list_todo_items():
    admin_token = get_token("admin")
    response = client.get("/api/todoitems", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 20
    items = sorted(data["items"], key=lambda x: x["message"])
    assert items[0]["message"] == "Paper Boat 1"
    assert items[10]["message"] == "Paper Crane 1"

    user_1_token = get_token("user1")
    response = client.get("/api/todoitems", headers={"Authorization": f"Bearer {user_1_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    items = sorted(data["items"], key=lambda x: x["message"])
    assert items[1]["message"] == "Paper Crane 10"


def test_create_todo_items(db):
    user_1 = db.query(models.User).filter_by(username="user1").one()
    user_1_token = get_token("user1")
    response = client.post(
        "/api/todoitems",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"todo_id": 1, "message": "Paper Crane 11"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Paper Crane 11"
    assert data["owner_id"] == user_1.id
    assert len(db.query(models.TodoItem).filter_by(owner_id=user_1.id).all()) == 11
    for i in range(10):
        response = client.post(
            "/api/todoitems",
            headers={"Authorization": f"Bearer {user_1_token}"},
            json={"todo_id": 1, "message": f"Paper Crane {11 + i}"},
        )
        assert len(db.query(models.TodoItem).filter_by(owner_id=user_1.id).all()) == 11 + (i + 1)


def test_get_todo_items():
    id = 15
    admin_token = get_token("admin")
    response = client.get(f"/api/todoitems/{id}", headers={"Authorization": f"Bearer {admin_token}"}, params={"id": id})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id

    id = 7
    user_1_token = get_token("user1")
    response = client.get(
        f"/api/todoitems/{id}", headers={"Authorization": f"Bearer {user_1_token}"}, params={"id": id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id

    user_2_token = get_token("user2")
    response = client.get(
        f"/api/todoitems/{id}", headers={"Authorization": f"Bearer {user_2_token}"}, params={"id": id}
    )
    assert response.status_code == 400


def test_update_todo_items():
    id = 1
    admin_token = get_token("admin")
    response = client.put(
        f"/api/todoitems/{id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"id": id},
        json={"message": "Paper Crane 11"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Paper Crane 11"

    user_1_token = get_token("user1")
    response = client.put(
        f"/api/todoitems/{id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        params={"id": id},
        json={"message": "Paper Crane 12"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Paper Crane 12"

    user_2_token = get_token("user2")
    response = client.put(
        f"/api/todoitems/{id}",
        headers={"Authorization": f"Bearer {user_2_token}"},
        params={"id": id},
        json={"message": "Paper Crane 13"},
    )
    assert response.status_code == 400


def test_delete_todo_item(db):
    id = 1
    admin_token = get_token("admin")
    todo_item = db.query(models.TodoItem).filter_by(id=1).one()
    response = client.delete(
        f"/api/todoitems/{id}", headers={"Authorization": f"Bearer {admin_token}"}, params={"id": id}
    )
    assert response.status_code == 200
    todo_items = db.query(models.TodoItem).all()
    assert todo_item not in todo_items

    id = 13
    user_1_token = get_token("user1")
    response = client.delete(
        f"/api/todoitems/{id}", headers={"Authorization": f"Bearer {user_1_token}"}, params={"id": id}
    )
    assert response.status_code == 400

    user_2_token = get_token("user2")
    todo_item = db.query(models.TodoItem).filter_by(id=id).one()
    response = client.delete(
        f"/api/todoitems/{id}", headers={"Authorization": f"Bearer {user_2_token}"}, params={"id": id}
    )
    assert response.status_code == 200
    todo_items = db.query(models.TodoItem).all()
    assert todo_item not in todo_items


def test_toggle_todo_item():
    id = 8
    admin_token = get_token("admin")
    response = client.put(
        f"/api/todoitems/{id}/toggle", headers={"Authorization": f"Bearer {admin_token}"}, params={"id": id}
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["active"]

    user_1_token = get_token("user1")
    response = client.put(
        f"/api/todoitems/{id}/toggle", headers={"Authorization": f"Bearer {user_1_token}"}, params={"id": id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"]

    user_2_token = get_token("user2")
    response = client.put(
        f"/api/todoitems/{id}/toggle", headers={"Authorization": f"Bearer {user_2_token}"}, params={"id": id}
    )
    assert response.status_code == 400
