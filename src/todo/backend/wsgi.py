import os
import logging
from fastapi.logger import logger as fastapi_logger

from todo.backend.app import init_app
from todo.backend.storage.database import Base, engine

app = init_app()

Base.metadata.create_all(bind=engine)

if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    gunicorn_logger = logging.getLogger("gunicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

    fastapi_logger.handlers = gunicorn_error_logger.handlers
    fastapi_logger.setLevel(gunicorn_logger.level)
