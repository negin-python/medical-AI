from sqlalchemy.orm import Session
from fastapi import HTTPException
from database.models import Regisration,RefreshToken,RestToken
from security.password import hash_password, verify_password
from security.jwt import create_access_token,create_refresh_token,verify_refresh_token
import secrets
from datetime import datetime,timezone,timedelta
from sqlalchemy import select
from exceptions.custom_exceptions import AppException

ROLE_PERMISSIONS = {
    "admin":
      ["patient:read",
       "patient:create",
       "patient:update",
       "patient:delete"],
    "doctor":
      ["patient:read",
       "patient:create",
       "patient:update"],
    "nurse": ["patient:read"],
}


def register(db: Session, username: str, password: str):

    user =select(Regisration).where(Regisration.username == username)
    if db.execute(user).scalar_one_or_none() is not None:
        raise AppException (status_code=400, 
                            message="username already exists",
                            error_code="USERNAME_ALREADY_EXISTS")

    new_user = Regisration(username=username, password=hash_password(password), role="nurse")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login(db: Session, username: str, password: str):

    query = select(Regisration).where(Regisration.username == username)
    user = db.execute(query).scalar_one_or_none()
    

    if user is None or not verify_password(password, user.password):
        raise AppException(status_code=401,
                           message="username or password is incorrect",
                           error_code="USERNAME OR PASSWORD IS INCORRECT")

    permissions = ROLE_PERMISSIONS.get(user.role, [])

    token = create_access_token({"username": user.username, "permissions": permissions})
    refresh_token_value = create_refresh_token({"username":user.username})

    new_refresh_token = RefreshToken(
        username = user.username,
        token = refresh_token_value,
        revoked = False
    )
    db.add(new_refresh_token)
    db.commit()

    return {"access_token": token,
            "refresh_token":refresh_token_value,
            "token_type": "bearer"}

def refresh_access_token(refresh_token:str,db:Session):
    payload = verify_refresh_token(refresh_token)

    if payload is None:
        raise AppException(
            status_code=401,
            message="invalid refresh token",
            error_code="INVALID REFERSH TOKEN"
        )
    if payload.get("token_type") != "refresh":
        raise AppException(
            status_code=401,
            message="invalid refresh token",
            error_code="INVALID REFERSH TOKEN"
        )
    stored = select(RefreshToken).where(
        RefreshToken.token == refresh_token
    )
    stored_token = db.execute(stored).scalar_one_or_none()

    if stored_token is None:
        raise AppException(
            status_code=401,
            message="refresh token not found",
            error_code="REFRESH TOKEN NOT FOUND"
        )

    if stored_token.revoked:
        raise AppException(
            status_code=401,
            message="refresh token revoked",
            error_code="REFRESH TOKEN REVOKED")

    username = payload.get("username")
    query =select(Regisration).where(Regisration.username ==username)
    user = db.execute(query).scalar_one_or_none()

    if user is None:
        raise AppException(
            status_code=401,
            message="user not found",
            error_code="USER NOT FOUND"
        )

    permissions = ROLE_PERMISSIONS.get(user.role, [])

    new_access_token = create_access_token({"username":username,"permissions":permissions})

    return {
        "access_token":new_access_token,
        "token_type":"bearer"
    }


def logout(db: Session, refresh_token: str):

    stored = select(RefreshToken).where(
        RefreshToken.token == refresh_token
    )
    stored_token = db.execute(stored).scalar_one_or_none()

    if stored_token is None:
        raise AppException(
            status_code=401,
            message="refresh token not found",
            error_code="REFRESH TOKEN NOT FOUND"
        )

    stored_token.revoked = True
    db.commit()

    return {
        "message": "logout successful"
    }

def create_password_token(db:Session,
                          username:str):

    query = select(Regisration).where(Regisration.username == username)
    user = db.execute(query).scalar_one_or_none()

    if user is None:
        raise AppException(
            status_code=404,
            message="user not found",
            error_code="USER NOT FOUND"
        )
    token = secrets.token_urlsafe(32)

    rest_token = RestToken(
        username = username,
        token = token,
        expries_at = datetime.now(timezone.utc)+timedelta(minutes=15),
        used = False

    )
    db.add(rest_token)
    db.commit()

    return{
        "message":"password reset token created",
        "reset_token:":rest_token
    }


def reset_password(db:Session,
                   token:str,
                   new_password:str):

    reset =select(RestToken).where(RestToken.token == token)
    reset_token = db.execute(reset).scalar_one_or_none()

    if reset_token is None:
        raise AppException(
            status_code=401,
            message="invalid reset token",
            error_code="INVALID RESET TOKEN"
        )

    if reset_token.used:
        raise AppException(
            status_code=401,
            message="reset token already used",
            error_code="RESET TOKEN ALREADY USED"
        )

    if reset_token.expried_at < datetime.now(timezone.utc):
        raise AppException(
            status_code=401,
            message="reset token expried",
            error_code="RESET TOKEN EXPRIED"
        )
    query = select(Regisration).where(Regisration.username == reset_token.username)
    user = db.execute(query).scalar_one_or_none()

    if user is None:
        raise AppException(
            status_code=404,
            message="user not found",
            error_code="USER NOT FOUND"
        )
    user.password = hash_password(new_password)
    reset_token.used = True
    db.commit()

    return {
        "message":"password reset successfuly"
    }

