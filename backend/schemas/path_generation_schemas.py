from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class LearnerType(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    RESEARCHER = "researcher"

class TimeAvailability(str, Enum):
    PART_TIME = "part_time"
    FULL_TIME = "full_time"
    INTENSIVE = "intensive"

class LearningDomain(str, Enum):
    AI_ML = "ai_ml"
    WEB_DEV = "web_dev"
    CYBERSECURITY = "cybersecurity"
    CLOUD_COMPUTING = "cloud_computing"
    FULL_STACK = "full_stack"

class PathGenerationRequest(BaseModel):
    learner_type: LearnerType
    time_availability: TimeAvailability
    learning_domain: LearningDomain
    study_weeks: int = 12
    user_id: int

class GeneratedPathResponse(BaseModel):
    success: bool
    path_id: Optional[int] = None
    path_data: Optional[Dict[str, Any]] = None
    message: str

class LearningPathData(BaseModel):
    path: List[Dict[str, Any]]
    weekly_schedule: Dict[str, List[Dict[str, Any]]]
    stats: Dict[str, Any]
    user_preferences: Dict[str, Any]