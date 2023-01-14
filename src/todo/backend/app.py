from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response

from todo.backend.storage.database import SessionLocal
from todo.backend.routes import todos, todo_items, users
from todo.backend.storage.models import User


async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


async def setup_bootstrap_admin():
    try:
        db = SessionLocal()
        admin_user = db.query(User).filter_by(username="admin").one_or_none()

        if admin_user is None:
            admin_user = User(username="admin", hashed_password=users.hash_password("admin"), role="admin")
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


def init_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(BaseHTTPMiddleware, dispatch=db_session_middleware)
    app.add_event_handler("startup", setup_bootstrap_admin)

    app.include_router(todos.router)
    app.include_router(todo_items.router)
    app.include_router(users.router)

    return app
