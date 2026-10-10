from fastapi import APIRouter,Depends
from schemas.user import LoginData
from database.connection import get_database
from services.auth_service import register,login,refresh_access_token,logout,create_password_token,reset_password
from schemas.patient import RestPasswordToken
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register")
def register_user(patient:LoginData,db=Depends(get_database)):
     return register(db=db,
                     username=patient.username,
                     password=patient.password)
   

@router.post("/login")
def login_user(from_data:OAuth2PasswordRequestForm=Depends(),
               db=Depends(get_database)):

     return login(db=db,
                  username=from_data.username,
                  password=from_data.password)
@router.post("/refresh")
def token_refresh(refresh_token:str,
                  db = Depends(get_database)):
     return refresh_access_token(db = db,
                                 refresh_token=refresh_token)

@router.post("/logout")
def logout_user(token_refresh:str,
                db=Depends(get_database)
                ):

     return logout(
          db=db,
          token_refresh=token_refresh
     )

@router.post("/forget_password")
def forget_password(username:str,
                    db = Depends(get_database)):

     return create_password_token(db=db,
                                  username=username)

@router.post("/reset_password")
def reset_password_user(data:RestPasswordToken,
                   db=Depends(get_database)):

     return reset_password(
          db=db,
          token = data.token,
          new_password=data.new_password
     )

