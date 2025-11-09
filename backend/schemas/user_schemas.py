from pydantic import BaseModel
from typing import Optional

class LoginCredentials(BaseModel):
    name: str
    password: str
    learner_type: Optional[str] = None

class LearnerUpdate(BaseModel):
    name: str
    learner_type: str