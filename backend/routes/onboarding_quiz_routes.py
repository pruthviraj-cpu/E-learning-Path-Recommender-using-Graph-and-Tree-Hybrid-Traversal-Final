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
    if not questions:
        return {"score": 0, "level": "Beginner", "learner_type": "beginner"}

    score = 0
    for idx, q in enumerate(questions):
        qid = str(idx) 
        if qid in req.answers:
            ans = req.answers[qid].strip().lower()
            correct = q["correct_answer"].strip().lower()
            if ans == correct:
                score += 1

    if score >= 4:
        level = "Advanced"
    elif 2 <= score < 4:
        level = "Intermediate"
    else:
        level = "Beginner"

    return {"score": score, "level": level, "learner_type": level.lower()}