from pydantic import BaseModel

class register_user(BaseModel):
    username: str
    email: str
    password: str

class login_user(BaseModel):
    email: str
    password: str

class request(BaseModel):
    user: str
    request: str