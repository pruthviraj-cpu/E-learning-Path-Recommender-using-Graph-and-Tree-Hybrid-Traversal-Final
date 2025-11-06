from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserActivityBase(BaseModel):
    action_type: str
    description: Optional[str] = None
    duration_seconds: Optional[int] = 0

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityResponse(UserActivityBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True