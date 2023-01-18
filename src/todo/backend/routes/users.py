from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from todo.backend.dependencies import get_db, get_current_user, get_storage_manager
from todo.backend.storage.models import User
from todo.backend.config import CONFIG
from todo.backend.storage.storage_manager import StorageManager

router = APIRouter(prefix="/api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationException(Exception):
    pass


class UserSchema(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True


class UserCreateSchema(BaseModel):
    username: str
    password: str


class UserUpdateSchema(BaseModel):
    role: Optional[str]
    password: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter_by(username=username).one_or_none()
    if user is None:
        raise AuthenticationException(f"User '{username}' doesn't exist")

    if not pwd_context.verify(password, user.hashed_password):
        raise AuthenticationException(f"Incorrect password for user '{username}'")

    return user


def create_oauth_token(claims: dict) -> str:
    return jwt.encode(claims, CONFIG.secret_key, algorithm=CONFIG.algorithm)


@router.post("/token", response_model=Token)
def create_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        authenticate_user(db, form_data.username, form_data.password)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=CONFIG.access_token_expire_minutes)

    token = create_oauth_token({"sub": form_data.username, "exp": datetime.utcnow() + access_token_expires})

    return {"access_token": token, "token_type": "bearer"}


@router.post("/users", response_model=UserSchema)
def create_user(request_data: UserCreateSchema, db: Session = Depends(get_db)):
    user = User(username=request_data.username, hashed_password=hash_password(request_data.password), role="user")
    db.add(user)

    try:
        db.flush()
    except IntegrityError as e:
        if "already exists" in str(e):
            raise HTTPException(400, detail=f"Username '{request_data.username}' already taken")
        raise

    return user


@router.get("/users/me", response_model=UserSchema)
def get_user_self(user: User = Depends(get_current_user)):
    return user


@router.put("/users/{id}", response_model=UserSchema)
def update_user(
    id: int,
    request_data: UserUpdateSchema,
    sm: StorageManager = Depends(get_storage_manager),
    user: User = Depends(get_current_user),
):
    update_data = request_data.dict(exclude_unset=True)

    if "password" in update_data:
        update_user = sm.get(User, {"id": id})
        if user.id != update_user.id:
            raise HTTPException(403, detail="Passwords can only be updated for same user as requester")

        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    if "role" in update_data:
        if user.role != "admin":
            raise HTTPException(403, detail="Roles can only be updated by admin users")

    return sm.update(User, {"id": id}, update_data)


# Authorization: Bearer <token>

# from fastapi import Request
# import inspect

# request = None

# def call_func(func):
#     args = {}
#     sig = inspect.signature(func)
#     for name, parameter in sig.parameters.items():
#         if issubclass(parameter.annotation, Request):
#             args[name] = request
#         elif isinstance(parameter.default, Depends):
#             args[name] = call_func(parameter.default.dependency)
#         else:
#             raise Exception("I have no idea what to do with this param")

#     return func(**args)

# call_func(get_user_self)
