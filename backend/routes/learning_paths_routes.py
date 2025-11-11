from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json

from itertools import zip_longest
from models.database import get_db
from services.quiz_generator import quiz_generator
from models.quiz_results import QuizResult
from models.topic_models import Topic
from schemas.quiz_results_schemas import QuizResultCreate, QuizResultResponse, QuizAnalytics
from schemas.quiz_schemas import QuizRequest, QuizResponse, ContentQuizRequest
from schemas.topic_schemas import ModuleContent,ModuleResponse,ReadingMaterial,Section,Project
from services.quiz_feedback_service import QuizFeedbackService
from schemas.quiz_feedbackresult_schemas import QuizFeedbackResponse, UserQuizHistory
learning_paths_router = APIRouter(
    prefix="/learningpaths",
    tags=["Learning Paths"]
)


@learning_paths_router.post("/user/{user_id}/assessment-results", response_model=QuizResultResponse)
async def save_assessment_results(
    user_id: int,
    results_data: QuizResultCreate,
    db: Session = Depends(get_db)
):
    """
    Save assessment results for a user with detailed quiz data
    """
    try:
        # Create new quiz result record
        db_quiz_result = QuizResult(
            user_id=user_id,
            module_id=results_data.module_id,
            topic=results_data.topic,
            num_questions=results_data.num_questions,
            difficulty_level=results_data.difficulty_level,
            score=results_data.score,
            correct_answers=results_data.correct_answers,
            completion_status=results_data.completion_status,
            quiz_data=results_data.quiz_data,
            user_answers=[answer.dict() for answer in results_data.user_answers],
            time_taken_seconds=results_data.time_taken_seconds,
            confidence_rating=results_data.confidence_rating
        )
        
        db.add(db_quiz_result)
        db.commit()
        db.refresh(db_quiz_result)
        
        print(f"✅ Saved assessment results: User {user_id}, Module {results_data.module_id}, Score {results_data.score}%")
        
        return db_quiz_result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving assessment results: {str(e)}")

@learning_paths_router.get("/user/{user_id}/quiz-results")
async def get_user_quiz_results(
    user_id: int,
    module_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get quiz results for a user, optionally filtered by module
    """
    try:
        query = db.query(QuizResult).filter(QuizResult.user_id == user_id)
        
        if module_id:
            query = query.filter(QuizResult.module_id == module_id)
        
        results = query.order_by(QuizResult.completed_at.desc()).limit(limit).all()
        
        return {
            "user_id": user_id,
            "total_results": len(results),
            "quiz_results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quiz results: {str(e)}")

@learning_paths_router.get("/user/{user_id}/quiz-analytics")
async def get_user_quiz_analytics(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for user's quiz performance
    """
    try:
        # Get all user's quiz results
        results = db.query(QuizResult).filter(QuizResult.user_id == user_id).all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No quiz results found for user")
        
        # Calculate analytics
        total_quizzes = len(results)
        average_score = sum(r.score for r in results) / total_quizzes
        best_score = max(r.score for r in results)
        
        # Find strongest and weakest topics
        topic_scores = {}
        for result in results:
            if result.topic not in topic_scores:
                topic_scores[result.topic] = []
            topic_scores[result.topic].append(result.score)
        
        topic_avg_scores = {topic: sum(scores)/len(scores) for topic, scores in topic_scores.items()}
        strongest_topic = max(topic_avg_scores.items(), key=lambda x: x[1])[0]
        weakest_topic = min(topic_avg_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate total learning time
        total_learning_time = sum(r.time_taken_seconds or 0 for r in results)
        
        # Calculate completion rate (assuming all saved quizzes are completed)
        completion_rate = 100.0  # Since we only save completed quizzes
        
        analytics = QuizAnalytics(
            total_quizzes_taken=total_quizzes,
            average_score=round(average_score, 2),
            best_score=best_score,
            weakest_topic=weakest_topic,
            strongest_topic=strongest_topic,
            total_learning_time=total_learning_time,
            completion_rate=completion_rate
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@learning_paths_router.get("/user/{user_id}/module/{module_id}/progress")
async def get_module_progress(
    user_id: int,
    module_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user's progress and performance for a specific module
    """
    try:
        results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id,
            QuizResult.module_id == module_id
        ).order_by(QuizResult.completed_at.desc()).all()
        
        if not results:
            return {
                "user_id": user_id,
                "module_id": module_id,
                "attempts": 0,
                "best_score": 0,
                "average_score": 0,
                "last_attempt": None,
                "improvement_trend": "no_data"
            }
        
        best_score = max(r.score for r in results)
        average_score = sum(r.score for r in results) / len(results)
        last_attempt = results[0].completed_at
        
        # Calculate improvement trend
        if len(results) >= 2:
            recent_scores = [r.score for r in results[:2]]
            if recent_scores[0] > recent_scores[1]:
                trend = "improving"
            elif recent_scores[0] < recent_scores[1]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "single_attempt"
        
        return {
            "user_id": user_id,
            "module_id": module_id,
            "attempts": len(results),
            "best_score": best_score,
            "average_score": round(average_score, 2),
            "last_attempt": last_attempt,
            "improvement_trend": trend,
            "recent_results": [
                {
                    "score": r.score,
                    "correct_answers": f"{r.correct_answers}/{r.num_questions}",
                    "completed_at": r.completed_at
                }
                for r in results[:5]  # Last 5 attempts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching module progress: {str(e)}")


# @learning_paths_router.get("/modules/{module_id}/content")
# async def get_module_content(module_id: str, db: Session = Depends(get_db)):
#     """
#     Get detailed content for a specific module
#     """
#     try:
#         # This would typically fetch from your database
#         # For now, returning mock data - replace with actual database queries
        
#         # Example module content structure
#         module_content = {
#             "id": module_id,
#             "title": f"Module {module_id}",
#             "description": f"Detailed content for module {module_id}",
#             "content": {
#                 "sections": [
#                     {
#                         "title": "Introduction",
#                         "content": f"This is the introduction section for module {module_id}..."
#                     },
#                     {
#                         "title": "Key Concepts", 
#                         "content": f"Here are the key concepts for module {module_id}..."
#                     }
#                 ],
#                 "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"  # Example video
#             },
#             "skills": ["Skill 1", "Skill 2", "Skill 3"],
#             "difficulty": "Intermediate"
#         }
        
#         return module_content
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching module content: {str(e)}")

@learning_paths_router.get("/modules/{module_id}/content", response_model=ModuleResponse)
async def get_module_content(module_id: str, db: Session = Depends(get_db)):
    module = db.query(Topic).filter(Topic.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    resources = module.resources or {}

    # Videos and quizzes
    long_videos = resources.get("Long_videos", [])
    short_videos = resources.get("Short_videos", [])
    quizzes = resources.get("quizzes", [])

    # Sections
    sections = [Section(title=t, content="") for t in module.subtopics or []]

    # Reading materials
    titles = resources.get("reading_material_titles", [])  # optional array of titles
    links = resources.get("reading_material", [])

    reading_materials = []
    for i, link in enumerate(links):
        title = titles[i] if i < len(titles) else link
        reading_materials.append(
            ReadingMaterial(title=title, link=link, content="")
        )


    # Projects
    projects = [
    Project(
        title=p.get("title", ""),
        description=p.get("description", ""),
        link=p.get("link")
    )
    for p in resources.get("projects", [])
]


    return ModuleResponse(
        id=module.id,
        title=module.title,
        content=ModuleContent(
            long_videos=long_videos,
            short_videos=short_videos,
            reading_materials=reading_materials,
            projects=projects,
            quizzes=quizzes,
            sections=sections,
            video_url=short_videos[0] if short_videos else None
        ),
        skills=getattr(module, 'skills', []),
        difficulty=str(getattr(module, 'difficulty', '0'))
    )




@learning_paths_router.get("/modules/{module_id}/assessments")
async def get_module_assessments(module_id: str):
    """ 
    Get AI-generated assessments for a specific module
    """
    try:
        if not quiz_generator:
            raise HTTPException(status_code=503, detail="AI quiz service is currently unavailable")
        
        print(f"🎯 Generating AI assessments for module: {module_id}")
        
        # Extract topic from module_id (convert snake_case to Title Case)
        topic = module_id.replace('_', ' ').title()
        
        # Generate quiz using AI
        quiz_data = quiz_generator.generate_quiz_by_topic(
            topic=topic,
            num_questions=5,
            difficulty="beginner",
            question_types=["mcq", "true_false"]
        )
        
        # Transform AI response to frontend format
        assessments = []
        for i, question in enumerate(quiz_data.get("questions", [])):
            assessment = {
                "id": f"ai_assessment_{i}",
                "type": question.get("type", "mcq"),
                "questions": [question.get("question", "")],
                "options": _get_options_from_ai_question(question),
                "correct_answer": _get_correct_answer_index(question),
                "explanation": question.get("explanation", "No explanation provided."),
                "points": 1
            }
            assessments.append(assessment)
        
        print(f"✅ Generated {len(assessments)} AI assessments for module {module_id}")
        
        return {
            "module_id": module_id,
            "module_topic": topic,
            "assessments": assessments,
            "source": "ai_generated",
            "total_questions": len(assessments),
            "quiz_title": quiz_data.get("quiz_title", f"Quiz about {topic}")
        }
        
    except Exception as e:
        print(f"❌ Error generating AI assessments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate assessments: {str(e)}")

def _get_options_from_ai_question(question: Dict[str, Any]) -> List[str]:
    """Extract options from AI-generated question"""
    question_type = question.get("type", "mcq")
    
    if question_type == "mcq":
        options = question.get("options", {})
        if isinstance(options, dict):
            return list(options.values())
        elif isinstance(options, list):
            return options
        else:
            return ["Option A", "Option B", "Option C", "Option D"]
    elif question_type == "true_false":
        return ["True", "False"]
    else:
        return ["Option A", "Option B", "Option C", "Option D"]

def _get_correct_answer_index(question: Dict[str, Any]) -> int:
    """Convert AI correct answer to index for frontend"""
    question_type = question.get("type", "mcq")
    correct_answer = question.get("correct_answer", "A")
    
    if question_type == "mcq":
        # Convert "A", "B", "C", "D" to 0, 1, 2, 3
        if isinstance(correct_answer, str):
            return {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_answer.upper(), 0)
        else:
            return int(correct_answer)
    elif question_type == "true_false":
        # Convert "true"/"false" to 0/1
        if isinstance(correct_answer, str):
            return 0 if correct_answer.lower() == "true" else 1
        else:
            return int(correct_answer)
    else:
        return 0

# Update the existing confidence rating endpoint to store in quiz results
@learning_paths_router.post("/user/{user_id}/confidence")
async def save_confidence_rating(
    user_id: int,
    confidence_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Save user's confidence rating for a module (can be linked to next quiz)
    """
    try:
        module_id = confidence_data.get('module_id')
        confidence_rating = confidence_data.get('confidence_rating')
        path_id = confidence_data.get('path_id')
        
        # Store confidence rating - you might want to create a separate table for this
        # or associate it with the next quiz attempt
        print(f"Saved confidence rating: User {user_id}, Module {module_id}, Rating {confidence_rating}")
        
        return {
            "success": True,
            "message": "Confidence rating saved successfully",
            "confidence_rating": confidence_rating
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving confidence rating: {str(e)}")

@learning_paths_router.post("/user/{user_id}/assessment-results")
async def save_assessment_results(
    user_id: int,
    results_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Save assessment results for a user
    """
    try:
        module_id = results_data.get('module_id')
        score = results_data.get('score')
        total_questions = results_data.get('total_questions')
        correct_answers = results_data.get('correct_answers')
        
        # Here you would save to database
        print(f"Saved assessment results: User {user_id}, Module {module_id}, Score {score}%")
        
        return {
            "success": True,
            "message": "Assessment results saved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving assessment results: {str(e)}")

# AI Quiz Generation Routes
@learning_paths_router.post("/ai/generate-quiz", response_model=QuizResponse)
async def generate_ai_quiz(quiz_request: QuizRequest):
    """
    Generate AI-powered quiz based on topic
    """
    if not quiz_generator:
        raise HTTPException(status_code=503, detail="AI service is currently unavailable")
    
    try:
        print(f"🎯 Generating AI quiz for topic: {quiz_request.topic}")
        print(f"📊 Parameters: {quiz_request.num_questions} questions, {quiz_request.difficulty} difficulty")
        
        quiz_data = quiz_generator.generate_quiz_by_topic(
            topic=quiz_request.topic,
            num_questions=quiz_request.num_questions,
            difficulty=quiz_request.difficulty,
            question_types=[qt.value for qt in quiz_request.question_types]
        )
        
        print(f"✅ Successfully generated quiz with {len(quiz_data.get('questions', []))} questions")
        return quiz_data
        
    except Exception as e:
        print(f"❌ Error generating AI quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@learning_paths_router.post("/ai/generate-quiz-from-content", response_model=QuizResponse)
async def generate_quiz_from_content(quiz_request: ContentQuizRequest):
    """
    Generate AI-powered quiz from provided content
    """
    if not quiz_generator:
        raise HTTPException(status_code=503, detail="AI service is currently unavailable")
    
    try:
        print(f"🎯 Generating AI quiz from content (length: {len(quiz_request.content)} chars)")
        
        quiz_data = quiz_generator.generate_quiz_from_content(
            content=quiz_request.content,
            num_questions=quiz_request.num_questions,
            question_types=[qt.value for qt in quiz_request.question_types]
        )
        
        print(f"✅ Successfully generated quiz from content with {len(quiz_data.get('questions', []))} questions")
        return quiz_data
        
    except Exception as e:
        print(f"❌ Error generating quiz from content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@learning_paths_router.post("/ai/generate-module-quiz/{module_id}")
async def generate_module_quiz(module_id: str, num_questions: int = 5):
    """
    Generate AI quiz for a specific module
    """
    if not quiz_generator:
        raise HTTPException(status_code=503, detail="AI service is currently unavailable")
    
    try:
        print(f"🎯 Generating AI quiz for module: {module_id}")
        
        # Extract topic from module_id
        topic = module_id.replace('_', ' ').title()
        
        # Generate quiz using AI
        quiz_data = quiz_generator.generate_quiz_by_topic(
            topic=topic,
            num_questions=num_questions,
            difficulty="beginner",
            question_types=["mcq", "true_false"]
        )
        
        # Transform for frontend
        transformed_questions = []
        for i, question in enumerate(quiz_data.get("questions", [])):
            transformed_question = {
                "id": f"module_quiz_{i}",
                "type": question.get("type", "mcq"),
                "questions": [question.get("question", "")],
                "options": _get_options_from_ai_question(question),
                "correct_answer": _get_correct_answer_index(question),
                "explanation": question.get("explanation", "No explanation provided."),
                "points": 1
            }
            transformed_questions.append(transformed_question)
        
        response_data = {
            "message": "Quiz generated successfully",
            "module_id": module_id,
            "module_topic": topic,
            "quiz": {
                "questions": transformed_questions,
                "quiz_title": quiz_data.get("quiz_title", f"Quiz about {topic}"),
                "total_questions": len(transformed_questions),
                "difficulty": "beginner"
            },
            "generated_at": "2024-01-01T00:00:00Z"  # You can use datetime.now().isoformat()
        }
        
        print(f"✅ Successfully generated module quiz with {len(transformed_questions)} questions")
        return response_data
        
    except Exception as e:
        print(f"❌ Error generating module quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate module quiz: {str(e)}")





@learning_paths_router.get("/user/{user_id}/quiz-feedback-by-id/{quiz_id}", response_model=QuizFeedbackResponse)
async def get_quiz_feedback_by_id(
    user_id: int,
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback for a specific quiz attempt by quiz ID
    """
    try:
        print(f"🔍 Fetching feedback for quiz ID: {quiz_id}, user ID: {user_id}")
        
        # Find the quiz result by ID
        quiz_result = db.query(QuizResult).filter(
            QuizResult.id == quiz_id,
            QuizResult.user_id == user_id
        ).first()
        
        if not quiz_result:
            raise HTTPException(
                status_code=404, 
                detail=f"No quiz found with ID {quiz_id} for user {user_id}"
            )
        
        # Generate feedback using the existing service
        quiz_data = quiz_result.quiz_data or {}
        quiz_title = quiz_data.get('quiz_title', f'Quiz - {quiz_result.topic}')
        
        feedback = QuizFeedbackService.get_quiz_feedback(db, user_id, quiz_title)
        
        if not feedback:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not generate feedback for quiz {quiz_id}"
            )
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving quiz feedback by ID: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving quiz feedback: {str(e)}"
        )

@learning_paths_router.get("/user/{user_id}/quiz-feedback/{quiz_title}", response_model=QuizFeedbackResponse)
async def get_quiz_feedback(
    user_id: int,
    quiz_title: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback for a specific quiz attempt by quiz title
    """
    try:
        print(f"🔍 Fetching feedback for quiz title: {quiz_title}, user ID: {user_id}")
        
        feedback = QuizFeedbackService.get_quiz_feedback(db, user_id, quiz_title)
        
        if not feedback:
            raise HTTPException(
                status_code=404, 
                detail=f"No quiz found with title '{quiz_title}' for user {user_id}"
            )
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving quiz feedback: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving quiz feedback: {str(e)}"
        )

@learning_paths_router.get("/user/{user_id}/quiz-history", response_model=List[UserQuizHistory])
async def get_user_quiz_history(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get user's quiz attempt history
    """
    try:
        history = QuizFeedbackService.get_user_quiz_history(db, user_id, limit)
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving quiz history: {str(e)}"
        )

@learning_paths_router.get("/user/{user_id}/quizzes")
async def get_user_quizzes(
    user_id: int,
    module_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all quizzes taken by a user with basic info
    """
    try:
        query = db.query(QuizResult).filter(QuizResult.user_id == user_id)
        
        if module_id:
            query = query.filter(QuizResult.module_id == module_id)
        
        results = query.order_by(QuizResult.completed_at.desc()).all()
        
        quizzes = []
        for result in results:
            quiz_data = result.quiz_data or {}
            quizzes.append({
                "id": result.id,
                "quiz_title": quiz_data.get('quiz_title', f'Quiz - {result.topic}'),
                "module_id": result.module_id,
                "topic": result.topic,
                "score": result.score,
                "correct_answers": result.correct_answers,
                "total_questions": result.num_questions,
                "difficulty_level": result.difficulty_level,
                "time_taken_seconds": result.time_taken_seconds,
                "confidence_rating": result.confidence_rating,
                "completed_at": result.completed_at.isoformat(),
                "question_types": quiz_data.get('question_types', [])
            })
        
        return {
            "user_id": user_id,
            "total_quizzes": len(quizzes),
            "quizzes": quizzes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching user quizzes: {str(e)}"
        )
    



@learning_paths_router.post("/ai/real-time-feedback")
async def get_real_time_feedback(
    feedback_request: Dict[str, Any]
):
    """
    Get real-time AI feedback for a single question answer
    """
    if not quiz_generator:
        raise HTTPException(status_code=503, detail="AI feedback service is currently unavailable")
    
    try:
        question_data = feedback_request.get('question_data')
        user_answer = feedback_request.get('user_answer')
        time_taken = feedback_request.get('time_taken')
        user_context = feedback_request.get('user_context', {})
        
        if not question_data or user_answer is None:
            raise HTTPException(status_code=400, detail="question_data and user_answer are required")
        
        print(f"🎯 Generating real-time feedback for question {question_data.get('id', 'unknown')}")
        
        feedback = quiz_generator.generate_real_time_feedback(
            question_data=question_data,
            user_answer=user_answer,
            time_taken=time_taken,
            user_context=user_context
        )
        
        return {
            "success": True,
            "feedback": feedback,
            "question_id": question_data.get('id', '')
        }
        
    except Exception as e:
        print(f"❌ Error generating real-time feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")

@learning_paths_router.post("/ai/quiz-summary-feedback")
async def get_quiz_summary_feedback(
    summary_request: Dict[str, Any]
):
    """
    Get comprehensive AI feedback after quiz completion
    """
    if not quiz_generator:
        raise HTTPException(status_code=503, detail="AI feedback service is currently unavailable")
    
    try:
        quiz_data = summary_request.get('quiz_data')
        user_answers = summary_request.get('user_answers', [])
        user_context = summary_request.get('user_context', {})
        
        if not quiz_data or not user_answers:
            raise HTTPException(status_code=400, detail="quiz_data and user_answers are required")
        
        print(f"🎯 Generating quiz summary feedback for {len(user_answers)} questions")
        
        summary = quiz_generator.generate_quiz_summary_feedback(
            quiz_data=quiz_data,
            user_answers=user_answers,
            user_context=user_context
        )
        
        return {
            "success": True,
            "summary": summary,
            "quiz_title": quiz_data.get('quiz_title', 'Unknown Quiz')
        }
        
    except Exception as e:
        print(f"❌ Error generating quiz summary feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@learning_paths_router.post("/user/{user_id}/submit-quiz-answer")
async def submit_quiz_answer(
    user_id: int,
    answer_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Submit a single quiz answer and get immediate AI feedback
    """
    try:
        question_data = answer_data.get('question_data')
        user_answer = answer_data.get('selected_option')
        time_taken = answer_data.get('time_taken')
        quiz_session_id = answer_data.get('quiz_session_id')
        
        # Get user context for personalized feedback
        user_context = await _get_user_context(user_id, db)
        
        # Generate real-time feedback
        feedback = quiz_generator.generate_real_time_feedback(
            question_data=question_data,
            user_answer=user_answer,
            time_taken=time_taken,
            user_context=user_context
        )
        
        # Store the answer temporarily (you might want to store in a session table)
        print(f"✅ User {user_id} submitted answer for question {question_data.get('id')}")
        
        return {
            "success": True,
            "feedback": feedback,
            "is_correct": feedback.get('is_correct', False),
            "question_id": question_data.get('id', '')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz answer: {str(e)}")

async def _get_user_context(user_id: int, db: Session) -> Dict[str, Any]:
    """Get user context for personalized feedback"""
    try:
        # Get user's recent performance
        recent_results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id
        ).order_by(QuizResult.completed_at.desc()).limit(5).all()
        
        if recent_results:
            avg_score = sum(r.score for r in recent_results) / len(recent_results)
            
            # Find weak areas
            weak_areas = []
            for result in recent_results:
                if result.score < 70:  # Consider scores below 70% as weak areas
                    weak_areas.append(result.topic)
            
            return {
                'previous_performance': round(avg_score, 2),
                'weak_areas': list(set(weak_areas))[:3],  # Top 3 unique weak areas
                'total_quizzes_taken': len(recent_results)
            }
        
        return {}
        
    except Exception as e:
        print(f"⚠️ Error getting user context: {e}")
        return {}