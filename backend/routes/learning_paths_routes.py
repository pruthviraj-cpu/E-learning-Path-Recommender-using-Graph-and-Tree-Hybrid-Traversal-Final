from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json

from models.database import get_db
from services.quiz_generator import quiz_generator
from schemas.quiz_schemas import QuizRequest, QuizResponse, ContentQuizRequest

learning_paths_router = APIRouter(
    prefix="/learningpaths",
    tags=["Learning Paths"]
)

@learning_paths_router.get("/modules/{module_id}/content")
async def get_module_content(module_id: str, db: Session = Depends(get_db)):
    """
    Get detailed content for a specific module
    """
    try:
        # This would typically fetch from your database
        # For now, returning mock data - replace with actual database queries
        
        # Example module content structure
        module_content = {
            "id": module_id,
            "title": f"Module {module_id}",
            "description": f"Detailed content for module {module_id}",
            "content": {
                "sections": [
                    {
                        "title": "Introduction",
                        "content": f"This is the introduction section for module {module_id}..."
                    },
                    {
                        "title": "Key Concepts", 
                        "content": f"Here are the key concepts for module {module_id}..."
                    }
                ],
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"  # Example video
            },
            "skills": ["Skill 1", "Skill 2", "Skill 3"],
            "difficulty": "Intermediate"
        }
        
        return module_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching module content: {str(e)}")

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

@learning_paths_router.post("/user/{user_id}/confidence")
async def save_confidence_rating(
    user_id: int,
    confidence_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Save user's confidence rating for a module
    """
    try:
        module_id = confidence_data.get('module_id')
        confidence_rating = confidence_data.get('confidence_rating')
        path_id = confidence_data.get('path_id')
        
        # Here you would save to database
        print(f"Saved confidence rating: User {user_id}, Module {module_id}, Rating {confidence_rating}")
        
        return {
            "success": True,
            "message": "Confidence rating saved successfully"
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

@learning_paths_router.get("/ai/health")
async def ai_health_check():
    """
    Check AI service status
    """
    return {
        "ai_service_available": quiz_generator is not None,
        "model": quiz_generator.model if quiz_generator else None,
        "status": "healthy" if quiz_generator else "unavailable",
        "message": "AI Quiz Generator Service"
    }

@learning_paths_router.get("/test")
async def test_route():
    """Test if learning paths router is working"""
    return {"message": "Learning paths router is working!"}

@learning_paths_router.get("/health")
async def health_check():
    """Check if AI quiz generator is available"""
    return {
        "status": "healthy",
        "ai_quiz_available": quiz_generator is not None,
        "message": "Learning paths API is running"
    }