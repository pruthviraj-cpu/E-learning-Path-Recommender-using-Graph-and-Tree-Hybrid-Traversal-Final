from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PathBase(BaseModel):
    title: str
    type: str
    estimated_time: float
    load: str
    difficulty: int
    resources: Dict[str, Any]
    embedding: List[float]
    prerequisites: List[str]
    subnodes: List[str]

class PathCreate(PathBase):
    pass

class PathResponse(PathBase):
    id: int

    class Config:
        orm_mode = True