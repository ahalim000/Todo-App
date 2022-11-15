import logging
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///todos"
app.config["SQLALCHEMY_ECHO"] = True
db.init_app(app)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    todo_items = db.relationship("TodoItem", back_populates="todo", cascade="all,delete", order_by="TodoItem.position")

    def to_dict(self):
        res = {"id": self.id, "name": self.name, "todo_items": [todo_item.to_dict() for todo_item in self.todo_items]}

        return res


class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String, nullable=False)
    todo_id = db.Column(db.Integer, db.ForeignKey(Todo.id))
    position = db.Column(db.Integer, db.Sequence("seq_todo_item_position"))
    active = db.Column(db.Boolean, nullable=False, default=True)
    todo = db.relationship("Todo", back_populates="todo_items")

    def to_dict(self):
        res = {
            "id": self.id,
            "message": self.message,
            "todo_id": self.todo_id,
            "position": self.position,
            "active": self.active,
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
    request_data = request.get_json()
    todo_item_id = request_data["todo_item_id"]
    swap_todo_item_id = request_data["swap_todo_item_id"]

    todo_item = db.session.query(TodoItem).filter_by(id=todo_item_id).filter_by(todo_id=id).one()
    swap_todo_item = db.session.query(TodoItem).filter_by(id=swap_todo_item_id).filter_by(todo_id=id).one()

    temp = todo_item.position
    todo_item.position = swap_todo_item.position
    swap_todo_item.position = temp

    db.session.add(todo_item)
    db.session.add(swap_todo_item)
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
    todo_item = TodoItem(todo_id=request_data["todo_id"], message=request_data["message"])
    db.session.add(todo_item)
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


with app.app_context():
    db.create_all()
