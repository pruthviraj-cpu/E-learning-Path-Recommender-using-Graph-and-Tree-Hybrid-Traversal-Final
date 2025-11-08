from fastapi import APIRouter
from pydantic import BaseModel
from services.quiz_logic import paraphrase_text, load_questions
from schemas.onboarding_quiz_schemas import AnswerRequest

onboarding_quiz_router = APIRouter(
    prefix="/onboarding_quiz",
    tags=["Onboarding Quiz Routes"]
)

@onboarding_quiz_router.get("/get-quiz/{domain}")
def get_quiz(domain: str):
    questions = load_questions(domain)
    if not questions:
        return {"error": "Invalid domain"}
    
    quiz = []
    for idx, q in enumerate(questions):
        quiz.append({
            "id": idx,
            "text": paraphrase_text(q["text"]),
            "options": {k: paraphrase_text(v) for k, v in q["options"].items()},
            "correct_answer": q["correct_answer"]
        })
    return {"domain": domain, "questions": quiz}

@onboarding_quiz_router.post("/submit-quiz")
def submit_quiz(req: AnswerRequest):
    questions = load_questions(req.domain)
    score = 0
    for idx, q in enumerate(questions):
        if str(idx) in req.answers and req.answers[str(idx)].lower() == q["correct_answer"].lower():
            score += 1

    if score <= 2:
        level = "Beginner"
    elif score <= 4:
        level = "Intermediate"
    else:
        level = "Advanced"

    return {
        "score": score,
        "level": level,
        "learner_type": level.lower()  
    }