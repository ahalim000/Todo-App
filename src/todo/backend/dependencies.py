from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session


from todo.backend.config import CONFIG
from todo.backend.storage.models import User
from todo.backend.storage.storage_manager import StorageManager


def get_db(request: Request):
    return request.state.db


def get_oauth2_scheme():
    return OAuth2PasswordBearer(tokenUrl="/api/token")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(get_oauth2_scheme())):
    credentials_exception = HTTPException(
        401, headers={"WWW-Authentication": "Bearer"}, detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token, CONFIG.secret_key, algorithms=[CONFIG.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter_by(username=username).one_or_none()

    if user is None:
        raise credentials_exception

    return user


def get_storage_manager(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return StorageManager(db, user)
