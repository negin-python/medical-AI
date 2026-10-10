from pydantic import BaseModel
from pydantic import BaseModel, ConfigDict


class LoginData(BaseModel):
     username:str
     password:str

class UserCreate(BaseModel):
    username: str
    password: str



class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)