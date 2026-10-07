from sqlmodel import SQLModel

class SigninRequest(SQLModel):
    username: str
    password: str
