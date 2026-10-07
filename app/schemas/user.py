from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional


class UserUpdate(SQLModel):
    username: Optional[str]
    email: Optional[EmailStr]
