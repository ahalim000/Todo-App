import functools
import logging
from typing import List
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///todos"
db.init_app(app)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    todo_items = db.relationship("TodoItem", back_populates="todo", cascade="all,delete")

    # ID_SEQUENCE = 0

    # def __init__(self, name: str):
    #     self.name = name
    #     self.id = self.ID_SEQUENCE
    #     self.__class__.ID_SEQUENCE += 1
    #     self.todo_items: List[TodoItem] = []

    # def add_todo_item(self, todo_item):
    #     self.todo_items.append(todo_item)
    #     todo_item.set_todo(self)

    # def to_dict(self):
    #     return {"id": self.id, "name": self.name}


class TodoItem(db.Model):
    __tablename__ = "todo_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String, nullable=False)
    todo_id = db.Column(db.Integer, db.ForeignKey(Todo.id))
    todo = db.relationship("Todo", back_populates="todo_items")

    # ID_SEQUENCE = 0

    # def __init__(self, message: str):
    #     self.id = self.ID_SEQUENCE
    #     self.__class__.ID_SEQUENCE += 1
    #     self.todo = None
    #     self.message = message

    # def set_todo(self, todo):
    #     self.todo = todo


# class DataManager:
#     def __init__(self):
#         self.todos: List[Todo] = []
#         self.todo_items: List[TodoItem] = []

#     def list_todos(self):
#         return self.todos

#     def create_todo(self, name):
#         todo = Todo(name)
#         self.todos.append(todo)

#         return todo


# @functools.lru_cache()
# def get_data_manager():
#     return DataManager()


# @app.route("/api/todos", methods=["GET"])
# def list_todos():
#     data_manager = get_data_manager()

#     response = {"items": []}
#     todos = data_manager.list_todos()
#     for todo in todos:
#         response["items"].append(todo.to_dict())

#     return response


# @app.route("/api/todos", methods=["POST"])
# def create_todo():
#     data_manager = get_data_manager()
#     name = request.get_json()["name"]
#     todo = data_manager.create_todo(name)

#     return todo.to_dict()
