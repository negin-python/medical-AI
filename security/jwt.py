from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from hospital_api.config import settings


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["token_type"] = "access"
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)

def create_refresh_token(data:dict):
    to_encode =data.copy()
    to_encode["token_type"] = "refresh"
    exprie = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp":exprie})
    return jwt.encode(to_encode,
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token,
                          settings.SECRET_KEY,
                          algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

def verify_refresh_token(token:str):
    try:
        payload = jwt.decode(token,
                             settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
