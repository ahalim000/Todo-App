import os


class Config:
    def __init__(self):
        self.secret_key: str = os.environ["TODO_SECRET_KEY"]
        self.algorithm: str = os.environ.get("TODO_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.environ.get("TODO_ACCESS_TOKEN_EXPIRE_MINUTES", "300"))
        self.database_url: str = os.environ["TODO_DATABASE_URL"]


CONFIG = Config()
