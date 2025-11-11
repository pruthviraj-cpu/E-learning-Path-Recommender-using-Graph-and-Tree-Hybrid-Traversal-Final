from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.quiz_results import QuizResult
from schemas.quiz_feedbackresult_schemas import QuizFeedbackResponse, QuestionFeedback, UserQuizHistory
import json
from datetime import datetime

class QuizFeedbackService:
    
    @staticmethod
    def get_quiz_feedback(db: Session, user_id: int, quiz_title: str) -> Optional[QuizFeedbackResponse]:
        """
        Get detailed feedback for a specific quiz attempt by user ID and quiz title
        """
        try:
            print(f"🔍 Searching for quiz: user_id={user_id}, quiz_title='{quiz_title}'")
            
            # First, try to find by exact quiz_title match in quiz_data
            quiz_results = db.query(QuizResult).filter(
                QuizResult.user_id == user_id
            ).all()
            
            target_quiz = None
            for quiz in quiz_results:
                quiz_data = quiz.quiz_data or {}
                stored_title = quiz_data.get('quiz_title', '').strip()
                search_title = quiz_title.strip()
                
                print(f"📝 Checking quiz: '{stored_title}' vs '{search_title}'")
                
                # Try exact match first
                if stored_title == search_title:
                    target_quiz = quiz
                    break
                # Try partial match (in case of URL encoding issues)
                elif search_title in stored_title or stored_title in search_title:
                    target_quiz = quiz
                    break
            
            if not target_quiz:
                print(f"❌ No quiz found with title '{quiz_title}' for user {user_id}")
                # Try to find by topic as fallback
                target_quiz = db.query(QuizResult).filter(
                    QuizResult.user_id == user_id,
                    QuizResult.topic.ilike(f"%{quiz_title}%")
                ).first()
                
                if not target_quiz:
                    print(f"❌ No quiz found with topic containing '{quiz_title}'")
                    return None
            
            print(f"✅ Found quiz: {target_quiz.topic}")
            
            # Parse quiz data and user answers
            quiz_data = target_quiz.quiz_data or {}
            user_answers = target_quiz.user_answers or []
            
            # Convert user_answers from string if needed
            if isinstance(user_answers, str):
                try:
                    user_answers = json.loads(user_answers)
                except json.JSONDecodeError:
                    user_answers = []
            
            print(f"📊 Quiz data: {len(quiz_data.get('questions', []))} questions")
            print(f"📝 User answers: {len(user_answers)} answers")
            
            # Generate question feedback
            question_feedback = []
            strengths = []
            areas_for_improvement = []
            
            for user_answer in user_answers:
                question_id = user_answer.get('question_id')
                question_data = QuizFeedbackService._find_question_by_id(quiz_data, question_id)
                
                if question_data:
                    feedback = QuizFeedbackService._create_question_feedback(
                        question_data, user_answer
                    )
                    question_feedback.append(feedback)
                    
                    # Track strengths and weaknesses
                    if feedback.is_correct:
                        # Extract key concept from question for strengths
                        concept = QuizFeedbackService._extract_concept(feedback.question_text)
                        if concept:
                            strengths.append(concept)
                    else:
                        # Extract key concept for improvement areas
                        concept = QuizFeedbackService._extract_concept(feedback.question_text)
                        if concept:
                            areas_for_improvement.append(concept)
            
            # Ensure we have some strengths and improvement areas
            if not strengths:
                strengths = ["Good attempt", "Completed the assessment"]
            if not areas_for_improvement and question_feedback:
                areas_for_improvement = ["Review all concepts", "Practice more questions"]
            
            # Remove duplicates and limit to top 3
            strengths = list(set(strengths))[:3]
            areas_for_improvement = list(set(areas_for_improvement))[:3]
            
            # Generate overall feedback
            overall_feedback = QuizFeedbackService._generate_overall_feedback(
                target_quiz.score, 
                len([q for q in question_feedback if q.is_correct]),
                len(question_feedback)
            )
            
            feedback_response = QuizFeedbackResponse(
                quiz_title=quiz_data.get('quiz_title', f'Quiz - {target_quiz.topic}'),
                user_id=user_id,
                module_id=target_quiz.module_id,
                topic=target_quiz.topic,
                total_questions=target_quiz.num_questions,
                correct_answers=target_quiz.correct_answers,
                score=target_quiz.score,
                time_taken_seconds=target_quiz.time_taken_seconds,
                confidence_rating=target_quiz.confidence_rating,
                completed_at=target_quiz.completed_at.isoformat(),
                question_feedback=question_feedback,
                strengths=strengths,
                areas_for_improvement=areas_for_improvement,
                overall_feedback=overall_feedback
            )
            
            print(f"✅ Generated feedback for {len(question_feedback)} questions")
            return feedback_response
            
        except Exception as e:
            print(f"❌ Error in get_quiz_feedback: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _extract_concept(question_text: str) -> str:
        """Extract key concept from question text"""
        # Simple concept extraction - you can enhance this
        keywords = ["HTML", "CSS", "JavaScript", "Python", "SQL", "React", "Node", "API", "Database", "Function", "Variable", "Loop", "Array", "Object"]
        for keyword in keywords:
            if keyword.lower() in question_text.lower():
                return keyword
        return question_text.split('?')[0][:30] + "..." if '?' in question_text else question_text[:30] + "..."
    
    @staticmethod
    def get_user_quiz_history(db: Session, user_id: int, limit: int = 10) -> List[UserQuizHistory]:
        """
        Get user's quiz attempt history
        """
        try:
            quiz_results = db.query(QuizResult).filter(
                QuizResult.user_id == user_id
            ).order_by(QuizResult.completed_at.desc()).limit(limit).all()
            
            history = []
            for result in quiz_results:
                quiz_data = result.quiz_data or {}
                history.append(UserQuizHistory(
                    quiz_title=quiz_data.get('quiz_title', f'Quiz - {result.topic}'),
                    module_id=result.module_id,
                    score=result.score,
                    correct_answers=result.correct_answers,
                    total_questions=result.num_questions,
                    completed_at=result.completed_at,
                    time_taken_seconds=result.time_taken_seconds
                ))
            
            return history
            
        except Exception as e:
            print(f"Error fetching user quiz history: {e}")
            return []
    
    @staticmethod
    def _find_question_by_id(quiz_data: Dict[str, Any], question_id: str) -> Optional[Dict[str, Any]]:
        """Find question data by question ID"""
        questions = quiz_data.get('questions', [])
        for question in questions:
            if str(question.get('id')) == str(question_id):
                return question
        return None
    
    @staticmethod
    def _create_question_feedback(question_data: Dict[str, Any], user_answer: Dict[str, Any]) -> QuestionFeedback:
        """Create detailed feedback for a single question"""
        question_type = question_data.get('type', 'mcq')
        user_selected_index = user_answer.get('selected_option', 0)
        correct_answer_index = question_data.get('correct_answer', 0)
        is_correct = user_answer.get('is_correct', False)
        
        # Get answer texts based on question type
        if question_type == 'mcq':
            options = question_data.get('options', [])
            if isinstance(options, dict):
                # Convert dict options to list
                options = list(options.values())
            user_answer_text = options[user_selected_index] if user_selected_index < len(options) else "Unknown"
            correct_answer_text = options[correct_answer_index] if correct_answer_index < len(options) else "Unknown"
        elif question_type == 'true_false':
            options = ['True', 'False']
            user_answer_text = options[user_selected_index] if user_selected_index < len(options) else "Unknown"
            correct_answer_text = options[correct_answer_index] if correct_answer_index < len(options) else "Unknown"
        else:
            user_answer_text = f"Selected option {user_selected_index}"
            correct_answer_text = f"Correct option {correct_answer_index}"
        
        # Get question text
        question_text = ""
        questions_list = question_data.get('questions', [])
        if questions_list:
            question_text = questions_list[0]
        elif 'question' in question_data:
            question_text = question_data['question']
        
        return QuestionFeedback(
            question_id=question_data.get('id', 'unknown'),
            question_text=question_text,
            user_answer=user_answer_text,
            correct_answer=correct_answer_text,
            is_correct=is_correct,
            explanation=question_data.get('explanation', 'No explanation available.'),
            time_taken=user_answer.get('time_taken'),
            user_selected_index=user_selected_index,
            correct_answer_index=correct_answer_index
        )
    
    @staticmethod
    def _generate_overall_feedback(score: int, correct_count: int, total_questions: int) -> str:
        """Generate overall feedback based on performance"""
        if total_questions == 0:
            return "No questions available for analysis."
            
        if score >= 90:
            return "Excellent work! You have demonstrated a strong understanding of this topic. Consider moving on to more advanced material."
        elif score >= 75:
            return "Good job! You have a solid grasp of the concepts. Review the areas you missed to further strengthen your knowledge."
        elif score >= 60:
            return "You're making good progress! Focus on the areas where you struggled to improve your overall understanding."
        else:
            return "This was a challenging assessment. Take time to review the material and don't get discouraged - learning is a journey!"