from pydantic import BaseModel
from typing import List, Dict


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    weights: Dict[str, int]


class QuizResponse(BaseModel):
    answers: List[int]


class LearnerResult(BaseModel):
    visual: int
    auditory: int
    kinesthetic: int
    learner_type: str