from datetime import datetime, timedelta
from todo.backend.routes.users import create_oauth_token


def get_token(username):
    return create_oauth_token({"sub": username, "exp": datetime.utcnow() + timedelta(minutes=60)})
