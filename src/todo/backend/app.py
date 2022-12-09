from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response

from todo.backend.storage.database import SessionLocal
from todo.backend.routes import todos
from todo.backend.routes import todo_items


async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


def init_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(BaseHTTPMiddleware, dispatch=db_session_middleware)

    app.include_router(todos.router)
    app.include_router(todo_items.router)

    return app
