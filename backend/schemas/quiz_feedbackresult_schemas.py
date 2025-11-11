from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class QuestionFeedback(BaseModel):
    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str
    time_taken: Optional[int] = None
    user_selected_index: int
    correct_answer_index: int

class QuizFeedbackResponse(BaseModel):
    quiz_title: str
    user_id: int
    module_id: str
    topic: str
    total_questions: int
    correct_answers: int
    score: int
    time_taken_seconds: Optional[int]
    confidence_rating: Optional[int]
    completed_at: str
    question_feedback: List[QuestionFeedback]
    strengths: List[str]
    areas_for_improvement: List[str]
    overall_feedback: str

class UserQuizHistory(BaseModel):
    quiz_title: str
    module_id: str
    score: int
    correct_answers: int
    total_questions: int
    completed_at: datetime
    time_taken_seconds: Optional[int]