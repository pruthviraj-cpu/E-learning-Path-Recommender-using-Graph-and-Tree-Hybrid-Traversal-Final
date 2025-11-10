# routes/gan_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List,Optional,Tuple
import json
import logging
from models.database import get_db
from models.user_models import User
from models.user_path_models import UserLearningPath
from models.quiz_results import QuizResult
from services.gan_forecaster import GANForecaster
from services.path_service import path_service 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gan", tags=["GAN Forecasting"])

# Initialize GAN Forecaster
gan_forecaster = GANForecaster(train_epochs=120,
                               path_service=path_service)

@router.get("/evaluate-path/{user_id}")
async def evaluate_learner_path(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Evaluate a learner's path using GAN forecasting
    """
    try:
        logger.info(f"🎯 Starting GAN evaluation for user: {user_id}")
        
        # Get user's active learning path
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            logger.warning(f"❌ No active learning path found for user {user_id}")
            raise HTTPException(status_code=404, detail="No active learning path found for user")
        
        logger.info(f"📁 Found path: {user_path.title}")
        
        # Convert user_id to string for GAN forecaster
        learner_id_str = str(user_id)
        
        # Evaluate path using GAN
        metrics = gan_forecaster.evaluate_path(learner_id_str)
        
        logger.info(f"✅ GAN evaluation completed for user {user_id}")
        
        return {
            "user_id": user_id,
            "path_title": user_path.title,
            "evaluation_metrics": metrics,
            "success_probability": metrics["success_probability"],
            "revision_advice": metrics["revision_advice"]
        }
        
    except Exception as e:
        logger.error(f"💥 Error evaluating path: {e}")
        raise HTTPException(status_code=500, detail=f"Error evaluating path: {str(e)}")

@router.get("/suggest-skips/{user_id}")
async def suggest_skippable_modules(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Suggest modules that can be safely skipped
    """
    try:
        logger.info(f"🔍 Finding skippable modules for user: {user_id}")
        
        # Verify user exists and has active path
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            logger.warning(f"❌ No active learning path found for user {user_id}")
            raise HTTPException(status_code=404, detail="No active learning path found for user")
        
        learner_id_str = str(user_id)
        suggestions = gan_forecaster.suggest_skips(learner_id_str)
        
        logger.info(f"✅ Found {len(suggestions)} skippable modules for user {user_id}")
        
        return {
            "user_id": user_id,
            "suggested_skips": suggestions,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"💥 Error generating skip suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating skip suggestions: {str(e)}")

@router.post("/analyze-skip/{user_id}")
async def analyze_module_skip(
    user_id: int, 
    module_title: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze whether a specific module can be safely skipped
    """
    try:
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            raise HTTPException(status_code=404, detail="No active learning path found for user")
        
        learner_id_str = str(user_id)
        analysis = gan_forecaster.should_skip_module(learner_id_str, module_title)
        
        return {
            "user_id": user_id,
            "module_analysis": analysis,
            "skip_recommended": analysis["skip_recommended"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing module skip: {str(e)}")

@router.get("/learner-progress/{user_id}")
async def get_learner_progress_metrics(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive learner progress metrics for GAN analysis
    """
    try:
        logger.info(f"📊 Fetching learner progress for user: {user_id}")
        
        # Get user's quiz results
        quiz_results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id
        ).all()
        logger.info(f"📈 Found {len(quiz_results)} quiz results")
        
        # Get user's learning path
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            logger.warning(f"❌ No active learning path found for user {user_id}")
            raise HTTPException(status_code=404, detail="No active learning path found")
        
        logger.info(f"📁 User path: {user_path.title}")
        
        # Calculate average quiz scores by module
        module_scores = {}
        for quiz in quiz_results:
            module_id = quiz.module_id or "unknown"
            if module_id not in module_scores:
                module_scores[module_id] = []
            module_scores[module_id].append(quiz.score)
        
        avg_scores = {
            module: sum(scores) / len(scores) 
            for module, scores in module_scores.items()
        }
        logger.info(f"📊 Calculated average scores for {len(avg_scores)} modules")
        
        # Calculate completion statistics
        completed_nodes = user_path.completed_nodes or []
        completed_modules = len(completed_nodes)
        
        # Handle different path data structures
        path_data = user_path.path_data
        if isinstance(path_data, dict) and 'path' in path_data:
            total_modules = len(path_data['path'])
        elif isinstance(path_data, list):
            total_modules = len(path_data)
        else:
            total_modules = 0
            logger.warning(f"❓ Unknown path data structure: {type(path_data)}")
        
        completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        logger.info(f"✅ Progress: {completed_modules}/{total_modules} modules ({completion_rate:.1f}%)")
        
        return {
            "user_id": user_id,
            "quiz_results_count": len(quiz_results),
            "average_scores_by_module": avg_scores,
            "completion_rate": round(completion_rate, 2),
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "current_week": user_path.current_week
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error fetching progress metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching progress metrics: {str(e)}")
    


@router.get("/debug/user-path/{user_id}")
async def debug_user_path(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Debug endpoint to check what user path data exists
    """
    try:
        # Get user's learning path
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            return {"error": "No active learning path found"}
        
        # Get user's quiz results
        quiz_results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id
        ).all()
        
        return {
            "user_id": user_id,
            "path_exists": True,
            "path_title": user_path.title,
            "path_data_type": type(user_path.path_data).__name__,
            "path_data_sample": str(user_path.path_data)[:500] if user_path.path_data else None,
            "weekly_schedule_type": type(user_path.weekly_schedule).__name__,
            "completed_nodes": user_path.completed_nodes,
            "quiz_results_count": len(quiz_results),
            "quiz_results_sample": [
                {
                    "module_id": q.module_id,
                    "topic": q.topic,
                    "score": q.score,
                    "difficulty_level": q.difficulty_level
                } for q in quiz_results[:3]  # First 3 results
            ] if quiz_results else []
        }
        
    except Exception as e:
        return {"error": f"Debug error: {str(e)}"}

@router.get("/debug/all-users")
async def debug_all_users(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Debug endpoint to see all users with their paths
    """
    try:
        users_with_paths = db.query(UserLearningPath).filter(
            UserLearningPath.is_active == 1
        ).all()
        
        users_info = []
        for path in users_with_paths:
            path_info = {
                "user_id": path.user_id,
                "path_title": path.title,
                "learner_type": path.learner_type,
                "learning_domain": path.learning_domain,
                "current_week": path.current_week,
                "progress_percentage": path.progress_percentage,
                "has_path_data": path.path_data is not None,
                "path_data_type": type(path.path_data).__name__ if path.path_data else None
            }
            
            # Handle different path data structures
            if path.path_data:
                if isinstance(path.path_data, dict):
                    path_info["path_data_keys"] = list(path.path_data.keys())
                    # Check if it has a 'path' key with list data
                    if 'path' in path.path_data and isinstance(path.path_data['path'], list):
                        path_info["path_nodes_count"] = len(path.path_data['path'])
                        path_info["sample_titles"] = [node.get('title', 'No title') for node in path.path_data['path'][:3]]
                    else:
                        path_info["path_nodes_count"] = "Unknown structure"
                        path_info["sample_titles"] = []
                elif isinstance(path.path_data, list):
                    path_info["path_nodes_count"] = len(path.path_data)
                    path_info["sample_titles"] = [node.get('title', 'No title') for node in path.path_data[:3]]
                else:
                    path_info["path_nodes_count"] = "Unknown type"
                    path_info["sample_titles"] = []
            else:
                path_info["path_nodes_count"] = 0
                path_info["sample_titles"] = []
                
            users_info.append(path_info)
        
        return {
            "total_active_paths": len(users_with_paths),
            "users": users_info
        }
    except Exception as e:
        return {"error": f"Debug error: {str(e)}"}


# routes/gan_routes.py - Add these new endpoints

@router.get("/quiz-performance-analysis/{user_id}")
async def analyze_quiz_performance(
    user_id: int, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze quiz performance over time and predict success probability
    """
    try:
        # Get user's quiz results within date range
        query = db.query(QuizResult).filter(QuizResult.user_id == user_id)
        
        if start_date:
            query = query.filter(QuizResult.completed_at >= start_date)
        if end_date:
            query = query.filter(QuizResult.completed_at <= end_date)
            
        quiz_results = query.order_by(QuizResult.completed_at).all()
        
        if not quiz_results:
            return {"error": "No quiz results found for the specified period"}
        
        # Analyze performance trends
        performance_data = []
        for quiz in quiz_results:
            performance_data.append({
                "timestamp": quiz.completed_at.isoformat() if quiz.completed_at else None,
                "module": quiz.module_id or quiz.topic,
                "score": quiz.score,
                "difficulty": quiz.difficulty_level,
                "time_taken": quiz.time_taken_seconds,
                "confidence": quiz.confidence_rating
            })
        
        # Calculate performance metrics
        scores = [q.score for q in quiz_results]
        avg_score = sum(scores) / len(scores)
        score_trend = _calculate_score_trend(quiz_results)
        consistency = _calculate_consistency(scores)
        
        # Predict success probability using GAN analysis
        learner_id_str = str(user_id)
        try:
            gan_metrics = gan_forecaster.evaluate_path(learner_id_str)
            success_probability = gan_metrics["success_probability"]
            revision_advice = gan_metrics["revision_advice"]
        except Exception as e:
            success_probability = 0.5  # Default if GAN fails
            revision_advice = {"message": "GAN analysis unavailable", "location": "none"}
        
        # Identify weak areas based on quiz performance
        weak_modules = _identify_weak_modules(quiz_results)
        
        # Generate revision recommendations
        revision_recommendations = _generate_revision_recommendations(
            weak_modules, 
            success_probability, 
            score_trend,
            db,
            user_id
        )
        
        return {
            "user_id": user_id,
            "analysis_period": {
                "start": start_date,
                "end": end_date,
                "total_quizzes": len(quiz_results)
            },
            "performance_metrics": {
                "average_score": round(avg_score, 2),
                "score_trend": score_trend,  # 'improving', 'declining', 'stable'
                "consistency": round(consistency, 2),  # 0-1, higher = more consistent
                "success_probability": round(success_probability, 4)
            },
            "weak_areas": weak_modules,
            "revision_recommendations": revision_recommendations,
            "quiz_performance_data": performance_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing quiz performance: {str(e)}")

@router.get("/predict-learning-gap/{user_id}")
async def predict_learning_gap(
    user_id: int,
    module_title: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict if a user will struggle with a specific module based on historical performance
    Automatically calculates date range based on module progression
    """
    try:
        logger.info(f"🎯 Predicting learning gap for user {user_id}, module: {module_title}")
        
        # Get user's learning path
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            return {"error": "No active learning path found"}
        
        # Find module in path and calculate date range
        target_module, date_range = _find_module_and_date_range(user_path, module_title, db, user_id)
        
        if not target_module:
            return {"error": f"Module '{module_title}' not found in user's path"}
        
        logger.info(f"📅 Using date range: {date_range['start_date']} to {date_range['end_date']}")
        
        # Get quiz results within calculated date range
        quiz_results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id,
            QuizResult.completed_at.between(date_range['start_date'], date_range['end_date'])
        ).all()
        
        logger.info(f"📊 Found {len(quiz_results)} quiz results in date range")
        
        # Analyze prerequisite performance
        prereq_performance = _analyze_prerequisite_performance(
            target_module, quiz_results, db, user_id
        )
        
        # Calculate struggle probability
        struggle_probability = _calculate_struggle_probability(prereq_performance, target_module)
        
        # Generate intervention recommendations
        interventions = _generate_intervention_recommendations(
            struggle_probability, 
            prereq_performance, 
            target_module
        )
        
        return {
            "user_id": user_id,
            "target_module": {
                "title": target_module.get('title'),
                "difficulty": target_module.get('difficulty'),
                "prerequisites": target_module.get('prerequisites', []),
                "position_in_path": date_range.get('module_position', 'unknown')
            },
            "analysis_period": {
                "start_date": date_range['start_date'].isoformat() if date_range['start_date'] else None,
                "end_date": date_range['end_date'].isoformat() if date_range['end_date'] else None,
                "timeframe_description": date_range['description']
            },
            "prerequisite_analysis": prereq_performance,
            "struggle_probability": round(struggle_probability, 4),
            "risk_level": _get_risk_level(struggle_probability),
            "recommended_interventions": interventions,
            "should_add_revision": struggle_probability > 0.7,
            "quiz_results_analyzed": len(quiz_results)
        }
        
    except Exception as e:
        logger.error(f"💥 Error predicting learning gap: {e}")
        raise HTTPException(status_code=500, detail=f"Error predicting learning gap: {str(e)}")

@router.post("/add-revision-node/{user_id}")
async def add_revision_node(
    user_id: int,
    revision_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add a revision node to user's learning path based on GAN analysis
    """
    try:
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path:
            raise HTTPException(status_code=404, detail="No active learning path found")
        
        # Create revision node
        revision_node = {
            "id": f"revision_{revision_data['target_module'].replace(' ', '_').lower()}",
            "title": f"Revision: {revision_data['target_module']}",
            "type": "revision",
            "estimated_time": revision_data.get('estimated_time', 4),
            "load": "light",
            "difficulty": revision_data.get('difficulty_adj', -1),  # Easier than target
            "prerequisites": [],
            "subnodes": [],
            "subtopics": ["Key concept review", "Common mistakes", "Practice exercises"],
            "resources": {
                "review_materials": revision_data.get('resources', []),
                "practice_quizzes": [f"{revision_data['target_module']}_review_quiz"]
            },
            "embedding": [0.1, 0.1, 0.1],  # Simple embedding for revision
            "is_revision": True
        }
        
        # Update user's path with revision node
        path_data = user_path.path_data
        if isinstance(path_data, dict) and 'path' in path_data:
            # Insert revision before target module
            new_path = []
            target_added = False
            for node in path_data['path']:
                if node.get('title') == revision_data['target_module'] and not target_added:
                    new_path.append(revision_node)
                    target_added = True
                new_path.append(node)
            path_data['path'] = new_path
        else:
            # Handle list format
            new_path = []
            target_added = False
            for node in path_data:
                if node.get('title') == revision_data['target_module'] and not target_added:
                    new_path.append(revision_node)
                    target_added = True
                new_path.append(node)
            path_data = new_path
        
        user_path.path_data = path_data
        db.commit()
        
        return {
            "user_id": user_id,
            "revision_node_added": revision_node['title'],
            "target_module": revision_data['target_module'],
            "message": "Revision node successfully added to learning path"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding revision node: {str(e)}")

# Helper functions for quiz analysis

def _calculate_score_trend(quiz_results: List[QuizResult]) -> str:
    """Calculate whether scores are improving, declining, or stable"""
    if len(quiz_results) < 3:
        return "insufficient_data"
    
    scores = [q.score for q in quiz_results]
    # Simple linear regression for trend
    x = list(range(len(scores)))
    slope = _linear_regression_slope(x, scores)
    
    if slope > 2:  # Improving
        return "improving"
    elif slope < -2:  # Declining
        return "declining"
    else:  # Stable
        return "stable"

def _linear_regression_slope(x, y):
    """Calculate slope of linear regression"""
    n = len(x)
    if n == 0:
        return 0
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    return numerator / denominator if denominator != 0 else 0

def _calculate_consistency(scores: List[float]) -> float:
    """Calculate consistency of scores (1 = perfectly consistent)"""
    if len(scores) < 2:
        return 1.0
    mean_score = sum(scores) / len(scores)
    variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
    max_variance = 2500  # Max variance for 0-100 scores
    return max(0, 1 - (variance / max_variance))

def _identify_weak_modules(quiz_results: List[QuizResult]) -> List[Dict[str, Any]]:
    """Identify modules where user performed poorly"""
    module_scores = {}
    for quiz in quiz_results:
        module = quiz.module_id or quiz.topic
        if module not in module_scores:
            module_scores[module] = []
        module_scores[module].append(quiz.score)
    
    weak_modules = []
    for module, scores in module_scores.items():
        avg_score = sum(scores) / len(scores)
        if avg_score < 70:  # Threshold for weak performance
            weak_modules.append({
                "module": module,
                "average_score": round(avg_score, 2),
                "attempts": len(scores),
                "improvement_needed": round(70 - avg_score, 2)
            })
    
    return sorted(weak_modules, key=lambda x: x['improvement_needed'], reverse=True)

def _generate_revision_recommendations(
    weak_modules: List[Dict[str, Any]], 
    success_probability: float,
    score_trend: str,
    db: Session,
    user_id: int
) -> List[Dict[str, Any]]:
    """Generate revision recommendations based on analysis"""
    recommendations = []
    
    # Add recommendations for weak modules
    for weak_module in weak_modules[:3]:  # Top 3 weakest
        recommendations.append({
            "type": "weak_area_revision",
            "module": weak_module['module'],
            "priority": "high" if weak_module['average_score'] < 60 else "medium",
            "action": f"Review {weak_module['module']} concepts",
            "estimated_time": 4,
            "reason": f"Low average score ({weak_module['average_score']}%)"
        })
    
    # Add trend-based recommendations
    if score_trend == "declining" and success_probability < 0.6:
        recommendations.append({
            "type": "trend_intervention",
            "module": "Recent topics",
            "priority": "high",
            "action": "Comprehensive review of recent modules",
            "estimated_time": 6,
            "reason": "Declining performance trend detected"
        })
    
    # Add success probability based recommendations
    if success_probability < 0.5:
        recommendations.append({
            "type": "foundational_review",
            "module": "Core concepts",
            "priority": "medium",
            "action": "Strengthen foundational knowledge",
            "estimated_time": 8,
            "reason": f"Low success probability ({success_probability:.2%})"
        })
    
    return recommendations

def _analyze_prerequisite_performance(
    target_module: Dict[str, Any],
    quiz_results: List[QuizResult],
    db: Session,
    user_id: int
) -> Dict[str, Any]:
    """Analyze performance on prerequisite modules"""
    prerequisites = target_module.get('prerequisites', [])
    prereq_performance = {}
    
    for prereq in prerequisites:
        # Find quiz results for this prerequisite
        prereq_quizzes = [q for q in quiz_results if q.module_id == prereq or q.topic == prereq]
        if prereq_quizzes:
            scores = [q.score for q in prereq_quizzes]
            avg_score = sum(scores) / len(scores)
            prereq_performance[prereq] = {
                "average_score": round(avg_score, 2),
                "attempts": len(prereq_quizzes),
                "mastery_level": "high" if avg_score >= 80 else "medium" if avg_score >= 60 else "low"
            }
        else:
            prereq_performance[prereq] = {
                "average_score": None,
                "attempts": 0,
                "mastery_level": "unknown"
            }
    
    return prereq_performance

def _calculate_struggle_probability(
    prereq_performance: Dict[str, Any],
    target_module: Dict[str, Any]
) -> float:
    """Calculate probability that user will struggle with target module"""
    if not prereq_performance:
        return 0.3  # Default moderate risk
    
    total_weight = 0
    struggle_score = 0
    
    for prereq, performance in prereq_performance.items():
        if performance['mastery_level'] == 'low':
            weight = 2.0
            struggle_score += weight * 0.8
        elif performance['mastery_level'] == 'medium':
            weight = 1.5
            struggle_score += weight * 0.5
        elif performance['mastery_level'] == 'high':
            weight = 1.0
            struggle_score += weight * 0.2
        else:  # unknown
            weight = 1.2
            struggle_score += weight * 0.6
        
        total_weight += weight
    
    # Adjust for target module difficulty
    target_difficulty = target_module.get('difficulty', 5)
    difficulty_factor = min(1.0, target_difficulty / 10)  # Normalize to 0-1
    
    base_probability = struggle_score / total_weight if total_weight > 0 else 0.5
    final_probability = base_probability * (0.7 + 0.3 * difficulty_factor)
    
    return min(0.95, final_probability)  # Cap at 95%

def _generate_intervention_recommendations(
    struggle_probability: float,
    prereq_performance: Dict[str, Any],
    target_module: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate intervention recommendations based on struggle probability"""
    interventions = []
    
    if struggle_probability > 0.7:
        # High risk - recommend revision before module
        weak_prereqs = [p for p, perf in prereq_performance.items() 
                       if perf.get('mastery_level') in ['low', 'unknown']]
        
        for prereq in weak_prereqs[:2]:  # Top 2 weakest
            interventions.append({
                "type": "prerequisite_revision",
                "module": prereq,
                "priority": "high",
                "action": f"Review {prereq} before starting {target_module.get('title')}",
                "estimated_time": 6,
                "reason": f"Weak prerequisite mastery ({prereq_performance[prereq].get('mastery_level', 'unknown')})"
            })
    
    if struggle_probability > 0.5:
        # Medium risk - recommend additional resources
        interventions.append({
            "type": "supplementary_materials",
            "module": target_module.get('title'),
            "priority": "medium",
            "action": "Study supplementary materials before starting module",
            "estimated_time": 4,
            "reason": f"Moderate struggle probability ({struggle_probability:.1%})"
        })
    
    return interventions

def _get_risk_level(probability: float) -> str:
    """Convert probability to risk level"""
    if probability >= 0.8:
        return "very_high"
    elif probability >= 0.7:
        return "high"
    elif probability >= 0.5:
        return "medium"
    elif probability >= 0.3:
        return "low"
    else:
        return "very_low"
    
def _find_module_and_date_range(user_path, module_title: str, db: Session, user_id: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Find target module and calculate appropriate date range for analysis
    """
    path_data = user_path.path_data
    actual_path = path_data.get('path', []) if isinstance(path_data, dict) else path_data
    
    target_module = None
    module_index = -1
    
    # Find the target module and its position
    for i, node in enumerate(actual_path):
        if node.get('title') == module_title or node.get('id') == module_title:
            target_module = node
            module_index = i
            break
    
    if not target_module:
        return None, {}
    
    # Calculate date range based on module position
    date_range = _calculate_analysis_date_range(module_index, actual_path, db, user_id)
    
    return target_module, date_range

def _calculate_analysis_date_range(module_index: int, path: List[Dict], db: Session, user_id: int) -> Dict[str, Any]:
    """
    Calculate appropriate date range for analyzing a module based on its position
    """
    from datetime import datetime, timedelta
    
    # Get user's first quiz date as reference
    first_quiz = db.query(QuizResult).filter(
        QuizResult.user_id == user_id
    ).order_by(QuizResult.completed_at.asc()).first()
    
    if not first_quiz or not first_quiz.completed_at:
        # Fallback: use last 30 days if no quiz history
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "description": "Last 30 days (no quiz history found)",
            "module_position": f"Position {module_index + 1} in path"
        }
    
    # Calculate based on module progression
    total_modules = len(path)
    progress_ratio = (module_index + 1) / total_modules if total_modules > 0 else 0
    
    # Get all quiz dates to understand learning pace
    all_quizzes = db.query(QuizResult).filter(
        QuizResult.user_id == user_id
    ).order_by(QuizResult.completed_at.asc()).all()
    
    if len(all_quizzes) < 2:
        # Not enough data, use reasonable default
        end_date = datetime.now()
        start_date = first_quiz.completed_at
        return {
            "start_date": start_date,
            "end_date": end_date,
            "description": f"From first quiz to now (module {module_index + 1}/{total_modules})",
            "module_position": f"Position {module_index + 1} in path"
        }
    
    # Calculate average time between quizzes
    time_diffs = []
    for i in range(1, len(all_quizzes)):
        diff = (all_quizzes[i].completed_at - all_quizzes[i-1].completed_at).days
        time_diffs.append(diff)
    
    avg_days_between = sum(time_diffs) / len(time_diffs) if time_diffs else 7
    
    # Estimate dates based on module position and learning pace
    start_date = first_quiz.completed_at
    estimated_days_to_module = module_index * avg_days_between * 2  # Conservative estimate
    
    analysis_start = start_date + timedelta(days=max(0, estimated_days_to_module - 14))  # 2 weeks before
    analysis_end = start_date + timedelta(days=estimated_days_to_module + 7)  # 1 week after
    
    # Cap at current date
    analysis_end = min(analysis_end, datetime.now())
    
    return {
        "start_date": analysis_start,
        "end_date": analysis_end,
        "description": f"Estimated period around module {module_index + 1}/{total_modules}",
        "module_position": f"Position {module_index + 1} in path",
        "estimated_completion": analysis_end.strftime("%Y-%m-%d") if analysis_end else None
    }