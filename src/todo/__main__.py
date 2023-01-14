#!/bin/env python3

import click
import json
import requests
from typing import Optional


# Client -> Server -> DB
# Client -> DB X
# (Many) Clients -> Server


@click.group()
def todo_cli():
    """
    Creates and manipulates todo lists and their items.
    """


@todo_cli.group()
def todos():
    """
    Creates and manipulates todo lists.
    """


@todos.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def list(url: str):
    request_url = f"{url}/api/todos"
    response = requests.get(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.option("-n", "--name", required=True, help="Name or description of todo list")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def create(url: str, name: str):
    request_url = f"{url}/api/todos"
    response = requests.post(request_url, json={"name": name})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def get(url: str, id: int):
    request_url = f"{url}/api/todos/{id}"
    response = requests.get(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-n", "--name", help="Name or description of todo list")
def update(url: str, id: int, name: str):
    request_url = f"{url}/api/todos/{id}"
    response = requests.put(request_url, json={"name": name})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def delete(url: str, id: int):
    request_url = f"{url}/api/todos/{id}"
    response = requests.delete(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todos.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-t", "--todo-item-id", required=True, help="ID of todo item", type=int)
@click.option("-i", "--insert-idx", required=True, help="Index that todo item will be inserted into", type=int)
def reorder(url: str, id: int, todo_item_id: int, insert_idx: int):
    request_url = f"{url}/api/todos/{id}/reorder"
    response = requests.put(request_url, json={"todo_item_id": todo_item_id, "insert_idx": insert_idx})
    response.raise_for_status()


@todo_cli.group()
def todo_items():
    """
    Creates and manipulates items in todo lists.
    """


@todo_items.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def list(url: str):
    request_url = f"{url}/api/todoitems"
    response = requests.get(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-id", "--todo_id", required=True, help="ID of todo in which todo item will be placed")
@click.option("-m", "--message", required=True, help="Description of task that needs to be done")
def create(url: str, todo_id: int, message: str):
    request_url = f"{url}/api/todoitems"
    response = requests.post(request_url, json={"todo_id": todo_id, "message": message})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def get(url: str, id: int):
    request_url = f"{url}/api/todoitems/{id}"
    response = requests.get(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
@click.option("-m", "--message", required=True, help="Description of task that needs to be done")
def update(url: str, id: int, message: str):
    request_url = f"{url}/api/todoitems/{id}"
    response = requests.put(request_url, json={"message": message})
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def delete(url: str, id: int):
    request_url = f"{url}/api/todoitems/{id}"
    response = requests.delete(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


@todo_items.command()
@click.argument("id")
@click.option("--url", default="http://127.0.0.1:8000", envvar="TODO_URL")
def toggle(url: str, id: int):
    request_url = f"{urlurl: str}/api/todoitems/{id}/toggle"
    response = requests.put(request_url)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))


if __name__ == "__main__":
    todo_cli()
