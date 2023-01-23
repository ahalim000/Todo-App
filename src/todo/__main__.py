#!/bin/env python3

import click
import json
import requests
from typing import Optional
from getpass import getpass


# Client -> Server -> DB
# Client -> DB X
# (Many) Clients -> Server


@click.group()
def todo_cli():
    """
    Creates and manipulates todo lists and their items.
    """


@todo_cli.group()
def tokens():
    """
    Creates tokens.
    """


@tokens.command()
@click.argument("username")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def create(url: str, username: str):
    request_url = f"{url}/api/token"
    response = requests.post(request_url, data={"username": username, "password": getpass()})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_cli.group()
def users():
    """
    Creates and manipulates users.
    """


@users.command()
@click.argument("username")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def create(url: str, username: str):
    request_url = f"{url}/api/users"
    response = requests.post(request_url, json={"username": username, "password": getpass()})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@users.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def get(id: str, url: str, token: str):
    request_url = f"{url}/api/users/{id}"
    response = requests.get(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@users.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option(
    "-r", "--role", help="New role for user. Can either be 'user' or 'admin'. Option only available to admin users."
)
@click.option("-p", "--password", help="New password for user")
@click.pass_context
def update(id: str, url: str, token: str, role: Optional[str], password: Optional[str]):
    request_url = f"{url}/api/users/{id}"

    data = {}
    if role:
        data["role"] = role
    if password:
        data["password"] = password

    response = requests.put(request_url, headers={"Authorization": f"Bearer {token}"}, json=data)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_cli.group()
def todos():
    """
    Creates and manipulates todo lists.
    """


@todos.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def list(url: str, token: str):
    request_url = f"{url}/api/todos"
    response = requests.get(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option("-n", "--name", required=True, help="Name or description of todo list")
def create(url: str, token: str, name: str):
    request_url = f"{url}/api/todos"
    response = requests.post(request_url, headers={"Authorization": f"Bearer {token}"}, json={"name": name})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def get(url: str, id: int, token: str):
    request_url = f"{url}/api/todos/{id}"
    response = requests.get(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option("-n", "--name", help="Name or description of todo list")
def update(url: str, id: int, token: str, name: str):
    request_url = f"{url}/api/todos/{id}"
    response = requests.put(request_url, headers={"Authorization": f"Bearer {token}"}, json={"name": name})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def delete(url: str, id: int, token: str):
    request_url = f"{url}/api/todos/{id}"
    response = requests.delete(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option("-tii", "--todo-item-id", required=True, help="ID of todo item", type=int)
@click.option("-ii", "--insert-idx", required=True, help="Index that todo item will be inserted into", type=int)
def reorder(url: str, id: int, token: str, todo_item_id: int, insert_idx: int):
    request_url = f"{url}/api/todos/{id}/reorder"
    response = requests.put(
        request_url,
        headers={"Authorization": f"Bearer {token}"},
        json={"todo_item_id": todo_item_id, "insert_idx": insert_idx},
    )
    response.raise_for_status()


@todo_cli.group()
def todo_items():
    """
    Creates and manipulates items in todo lists.
    """


@todo_items.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option(
    "-tid", "--todo_id", help="ID of todo whose items will be listed. If not given, items of all todos will be listed."
)
def list(url: str, token: str, todo_id: int):
    request_url = f"{url}/api/todoitems"

    filters = {}
    if todo_id:
        filters["todo_id"] = todo_id

    response = requests.get(request_url, headers={"Authorization": f"Bearer {token}"}, params=filters)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option("-tid", "--todo_id", required=True, help="ID of todo in which todo item will be placed")
@click.option("-m", "--message", required=True, help="Description of task that needs to be done")
def create(url: str, token: str, todo_id: int, message: str):
    request_url = f"{url}/api/todoitems"
    response = requests.post(
        request_url, headers={"Authorization": f"Bearer {token}"}, json={"todo_id": todo_id, "message": message}
    )
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def get(url: str, id: int, token: str):
    request_url = f"{url}/api/todoitems/{id}"
    response = requests.get(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
@click.option("-m", "--message", required=True, help="Description of task that needs to be done")
def update(url: str, id: int, token: str, message: str):
    request_url = f"{url}/api/todoitems/{id}"
    response = requests.put(request_url, headers={"Authorization": f"Bearer {token}"}, json={"message": message})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def delete(url: str, id: int, token: str):
    request_url = f"{url}/api/todoitems/{id}"
    response = requests.delete(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--token", required=True, envvar="TODO_TOKEN", help="Token required to authorize this command")
def toggle(url: str, id: int, token: str):
    request_url = f"{url}/api/todoitems/{id}/toggle"
    response = requests.put(request_url, headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


if __name__ == "__main__":
    todo_cli()
