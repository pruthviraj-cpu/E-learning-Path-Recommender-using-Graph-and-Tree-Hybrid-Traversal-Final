from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class UserAnswer(BaseModel):
    question_id: str
    selected_option: int  # index of selected option
    is_correct: bool
    time_taken: Optional[int] = None  # seconds for this question

class QuizResultCreate(BaseModel):
    user_id: int
    module_id: str
    topic: str
    num_questions: int
    difficulty_level: str
    score: int
    correct_answers: int
    completion_status: str = "completed"
    quiz_data: Optional[Dict[str, Any]] = None
    user_answers: List[UserAnswer]
    time_taken_seconds: Optional[int] = None
    confidence_rating: Optional[int] = None

class QuizResultResponse(BaseModel):
    id: int
    user_id: int
    module_id: str
    topic: str
    num_questions: int
    difficulty_level: str
    score: int
    correct_answers: int
    completion_status: str
    completed_at: datetime
    time_taken_seconds: Optional[int]
    confidence_rating: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class QuizAnalytics(BaseModel):
    total_quizzes_taken: int
    average_score: float
    best_score: int
    weakest_topic: str
    strongest_topic: str
    total_learning_time: int  # in seconds
    completion_rate: float