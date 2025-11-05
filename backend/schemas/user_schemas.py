from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginCredentials(BaseModel):
    name: str
    password: str