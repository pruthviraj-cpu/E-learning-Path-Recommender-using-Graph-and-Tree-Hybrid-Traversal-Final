# from fastapi import APIRouter
# from schemas.learner_type_quiz_schemas import QuizResponse, LearnerResult
# from services.learner_type_quiz_logic import load_and_paraphrase_quiz, evaluate_learner_type

# learner_quiz_router = APIRouter(
#     prefix="/learner-quiz", 
#     tags=["Learner Quiz"])

# # Cache quiz on load
# quiz_cache = load_and_paraphrase_quiz()

# @learner_quiz_router.get("/questions")
# def get_quiz_questions():
#     """Get paraphrased quiz questions"""
#     return quiz_cache


# @learner_quiz_router.post("/submit", response_model=LearnerResult)
# def submit_quiz(responses: QuizResponse):
#     """Submit learner quiz answers and get learner type"""
#     result = evaluate_learner_type(quiz_cache, responses.answers)
#     return result