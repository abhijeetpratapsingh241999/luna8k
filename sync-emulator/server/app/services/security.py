import secrets
from fastapi import Header, HTTPException, status

_API_KEY = secrets.token_hex(16)

def get_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != _API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def current_api_key() -> str:
    return _API_KEY
