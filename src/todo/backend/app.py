import logging
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
import string

from typing import List, Optional

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///todos"
app.config["SQLALCHEMY_ECHO"] = True
db.init_app(app)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

MAX_RANK_LENGTH = 128


def convert_base(
    num_s: str,
    target_base: int,
    current_base: int = 10,
    current_alphabet: str = "0123456789" + string.ascii_uppercase,
    target_alphabet: str = "0123456789" + string.ascii_uppercase,
) -> str:

    base_10 = 0
    digit = len(num_s) - 1
    for character in num_s:
        character_val = current_alphabet.index(character)
        base_10 += (current_base**digit) * character_val
        digit -= 1

    converted_num = ""
    floored_quotient = base_10
    while floored_quotient != 0:
        converted_num = target_alphabet[floored_quotient % target_base] + converted_num
        floored_quotient //= target_base

    if converted_num == "":
        converted_num = target_alphabet[0]

    return converted_num


def get_lexical_average(string1: str, string2: str) -> str:
    base10_string1 = int(convert_base(string1, 10, 26, string.ascii_lowercase))
    base10_string2 = int(convert_base(string2, 10, 26, string.ascii_lowercase))

    avg = (base10_string1 + base10_string2) // 2

    return convert_base(str(avg), 26, 10, target_alphabet=string.ascii_lowercase)


def get_lexical_rank(string1, string2):
    if string1.startswith("a") or string2.startswith("a"):
        raise Exception(f'Cannot get lexical rank for strings that begin with "a". Was given {string1} and {string2}.')

    max_len = max(len(string1), len(string2))

    while len(string1) < max_len:
        string1 += "a"

    while len(string2) < max_len:
        string2 += "a"

    lex_avg = get_lexical_average(string1, string2)

    if lex_avg == string1:
        lex_avg += "n"

    return lex_avg


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    todo_items = db.relationship(
        "TodoItem", back_populates="todo", cascade="all, delete-orphan", order_by="TodoItem.position"
    )

    def rerank_todo_items(self):
        self.todo_items[0].position = "b"
        self.todo_items[-1].position = "z"

        self._rerank_todo_items(0, len(self.todo_items) - 1)

    def _rerank_todo_items(self, start_idx, end_idx):
        if end_idx - start_idx <= 1:
            return

        mid_idx = (start_idx + end_idx) // 2
        mid_ti = self.todo_items[mid_idx]
        mid_ti.position = get_lexical_rank(self.todo_items[start_idx].position, self.todo_items[end_idx].position)

        self._rerank_todo_items(start_idx, mid_idx)
        self._rerank_todo_items(mid_idx, end_idx)

    def to_dict(self):
        todo_items = [todo_item.to_dict() for todo_item in self.todo_items]
        for idx, todo_item in enumerate(todo_items):
            todo_item["index"] = idx

        res = {"id": self.id, "name": self.name, "todo_items": todo_items}

        return res


class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String, nullable=False)
    todo_id = db.Column(db.Integer, db.ForeignKey(Todo.id))
    position = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    todo = db.relationship("Todo", back_populates="todo_items")

    def to_dict(self):
        res = {
            "id": self.id,
            "message": self.message,
            "todo_id": self.todo_id,
            "active": self.active,
            "position": self.position,
        }

        return res


@app.route("/api/todos", methods=["GET"])
def list_todos():
    todos = []
    for todo in db.session.query(Todo):
        todos.append(todo.to_dict())

    return {"items": todos}


@app.route("/api/todos", methods=["POST"])
def create_todo():
    request_data = request.get_json()
    todo = Todo(name=request_data["name"])
    db.session.add(todo)
    # INSERT INTO todo (name) VALUES ('First Todo') RETURNING todo.id
    db.session.commit()
    # SELECT todo_item.id AS todo_item_id, todo_item.message AS todo_item_message, todo_item.todo_id AS todo_item_todo_id, todo_item.position AS todo_item_position
    # FROM todo_item
    # WHERE todo_item.todo_id = 1
    # ORDER BY todo_item.position
    return todo.to_dict()


@app.route("/api/todos/<int:id>", methods=["GET"])
def get_todo(id):
    todo = db.session.query(Todo).filter_by(id=id).one()

    return todo.to_dict()


@app.route("/api/todos/<int:id>", methods=["PUT"])
def update_todo(id):
    todo = db.session.query(Todo).filter_by(id=id).one()
    request_data = request.get_json()
    todo.name = request_data["name"]
    db.session.add(todo)
    db.session.commit()

    return todo.to_dict()


@app.route("/api/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = db.session.query(Todo).filter_by(id=id).one()
    db.session.delete(todo)
    db.session.commit()

    return todo.to_dict()


@app.route("/api/todos/<int:id>/reorder", methods=["PUT"])
def reorder_todo(id):
    todo: Todo = db.session.query(Todo).filter_by(id=id).one()
    request_data = request.get_json()
    todo_item_id = request_data["todo_item_id"]
    insert_idx = request_data["insert_idx"]

    if insert_idx < 0:
        insert_idx = 0
    if insert_idx >= len(todo.todo_items):
        insert_idx = len(todo.todo_items) - 1

    todo_item: TodoItem = db.session.query(TodoItem).filter_by(id=todo_item_id).filter_by(todo_id=id).one()
    todo_idx = todo.todo_items.index(todo_item)

    todo.todo_items.pop(todo_idx)
    todo.todo_items.insert(insert_idx, todo_item)

    if len(todo.todo_items) == 1:
        return Response(status=201)

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

    db.session.add(todo)
    db.session.commit()

    return Response(status=201)


@app.route("/api/todoitems", methods=["GET"])
def list_todo_items():
    todo_items = []
    for todo_item in db.session.query(TodoItem):
        todo_items.append(todo_item.to_dict())

    return {"items": todo_items}


@app.route("/api/todoitems", methods=["POST"])
def create_todo_items():
    request_data = request.get_json()
    todo = db.session.query(Todo).filter_by(id=request_data["todo_id"]).one()
    todo_item = TodoItem(todo_id=request_data["todo_id"], message=request_data["message"])

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
        db.session.add(prev_last)

    db.session.add(todo_item)
    db.session.commit()

    if needs_reorder:
        db.session.refresh(todo)
        todo.rerank_todo_items()
        db.session.add(todo)
        db.session.commit()

    return todo_item.to_dict()


@app.route("/api/todoitems/<int:id>", methods=["GET"])
def get_todo_item(id):
    todo_item = db.session.query(TodoItem).filter_by(id=id).one()

    return todo_item.to_dict()


@app.route("/api/todoitems/<int:id>", methods=["PUT"])
def update_todo_item(id):
    todo_item = db.session.query(TodoItem).filter_by(id=id).one()
    request_data = request.get_json()
    todo_item.message = request_data["message"]
    db.session.add(todo_item)
    db.session.commit()

    return todo_item.to_dict()


@app.route("/api/todoitems/<int:id>", methods=["DELETE"])
def delete_todo_item(id):
    todo_item = db.session.query(TodoItem).filter_by(id=id).one()
    db.session.delete(todo_item)
    db.session.commit()

    return todo_item.to_dict()


@app.route("/api/todoitems/<int:id>/toggle", methods=["PUT"])
def toggle_todo_item(id):
    todo_item = db.session.query(TodoItem).filter_by(id=id).one()
    todo_item.active = not todo_item.active
    db.session.add(todo_item)
    db.session.commit()

    return todo_item.to_dict()
