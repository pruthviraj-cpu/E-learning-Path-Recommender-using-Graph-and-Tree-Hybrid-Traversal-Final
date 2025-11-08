from pydantic import BaseModel

class AnswerRequest(BaseModel):
    domain: str
    answers: dict 