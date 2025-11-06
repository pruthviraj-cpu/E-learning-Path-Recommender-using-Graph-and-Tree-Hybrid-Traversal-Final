from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TopicBase(BaseModel):
    title: str
    type: str
    estimated_time: float
    load: str
    difficulty: int
    resources: Dict[str, Any]
    embedding: List[float]
    prerequisites: List[str]
    subtopics: List[str]

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int

    class Config:
        from_attributes = True