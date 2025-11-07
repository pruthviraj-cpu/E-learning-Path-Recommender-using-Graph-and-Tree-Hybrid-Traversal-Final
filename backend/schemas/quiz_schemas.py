from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class QuestionType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_BLANK = "fill_blank"

class QuizRequest(BaseModel):
    topic: str = Field(..., description="Topic for quiz generation")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    difficulty: DifficultyLevel = Field(DifficultyLevel.BEGINNER, description="Difficulty level")
    question_types: List[QuestionType] = Field([QuestionType.MCQ], description="Types of questions")

class ContentQuizRequest(BaseModel):
    content: str = Field(..., description="Content to generate quiz from")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    question_types: List[QuestionType] = Field([QuestionType.MCQ], description="Types of questions")

class QuizResponse(BaseModel):
    quiz_title: str
    topic: str
    difficulty: str
    questions: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]