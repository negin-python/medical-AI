from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from security.jwt import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="invalid token")
    return payload


def require_permission(permission: str):
    def checker(user=Depends(get_token)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return checker