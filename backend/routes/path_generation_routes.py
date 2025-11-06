from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from services.path_service import path_service
from schemas.path_generation_schemas import (
    PathGenerationRequest, 
    GeneratedPathResponse,
    LearningPathData
)
from models.database import get_db
from models.user_models import User
from models.user_path_models import UserLearningPath  # New model

path_generation_router = APIRouter(
    prefix="/generate-path",
    tags=["Path Generation"]
)

@path_generation_router.post("/", response_model=GeneratedPathResponse)
async def generate_learning_path(
    request: PathGenerationRequest, 
    db: Session = Depends(get_db)
):
    """
    Generate a personalized learning path based on user preferences
    and save it to the user's profile with complete path data
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"🚀 Starting path generation for user {user.id}")
        
        # Generate learning path
        path_data = path_service.generate_learning_path(
            learner_type=request.learner_type.value,
            time_availability=request.time_availability.value,
            learning_domain=request.learning_domain.value,
            study_weeks=request.study_weeks
        )
        
        # Deactivate any existing active paths for this user
        db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user.id,
            UserLearningPath.is_active == 1
        ).update({"is_active": 0})
        
        # Create new user learning path with complete data
        new_user_path = UserLearningPath(
            user_id=user.id,
            title=f"{request.learning_domain.value.replace('_', ' ').title()} Path - {request.learner_type.value.title()}",
            description=f"Personalized learning path for {request.learner_type.value} level in {request.learning_domain.value.replace('_', ' ')}",
            
            # Store user preferences
            learner_type=request.learner_type.value,
            time_availability=request.time_availability.value,
            learning_domain=request.learning_domain.value,
            study_weeks=request.study_weeks,
            
            # Store complete path data
            path_data=path_data['path'],
            weekly_schedule=path_data['weekly_schedule'],
            stats=path_data['stats'],
            
            # Initialize progress
            current_week=1,
            completed_nodes=[],
            progress_percentage=0,
            is_active=1
        )
        
        db.add(new_user_path)
        db.commit()
        db.refresh(new_user_path)
        
        print(f"✅ Path generated and saved with ID: {new_user_path.id}")
        print(f"📊 Path stats: {len(path_data['path'])} nodes, {path_data['stats']['total_hours_used']} hours")
        
        return GeneratedPathResponse(
            success=True,
            path_id=new_user_path.id,
            path_data=path_data,
            message=f"Learning path generated successfully with {len(path_data['path'])} nodes"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating path: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")

@path_generation_router.get("/user/{user_id}/current-path")
async def get_user_current_path(user_id: int, db: Session = Depends(get_db)):
    """
    Get the current active learning path for a user with complete details
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_path = db.query(UserLearningPath).filter(
        UserLearningPath.user_id == user_id,
        UserLearningPath.is_active == 1
    ).first()
    
    if not current_path:
        return {
            "success": True, 
            "has_path": False, 
            "message": "No active learning path found"
        }
    
    return {
        "success": True,
        "has_path": True,
        "path": {
            "id": current_path.id,
            "title": current_path.title,
            "description": current_path.description,
            "learner_type": current_path.learner_type,
            "time_availability": current_path.time_availability,
            "learning_domain": current_path.learning_domain,
            "study_weeks": current_path.study_weeks,
            "path_data": current_path.path_data,
            "weekly_schedule": current_path.weekly_schedule,
            "stats": current_path.stats,
            "current_week": current_path.current_week,
            "completed_nodes": current_path.completed_nodes,
            "progress_percentage": current_path.progress_percentage,
            "created_at": current_path.created_at
        }
    }

@path_generation_router.get("/user/{user_id}/path/{path_id}/details")
async def get_path_details(user_id: int, path_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific learning path
    """
    path = db.query(UserLearningPath).filter(
        UserLearningPath.id == path_id,
        UserLearningPath.user_id == user_id
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    return {
        "success": True,
        "path": {
            "id": path.id,
            "title": path.title,
            "description": path.description,
            "learner_type": path.learner_type,
            "time_availability": path.time_availability,
            "learning_domain": path.learning_domain,
            "study_weeks": path.study_weeks,
            "path_data": path.path_data,
            "weekly_schedule": path.weekly_schedule,
            "stats": path.stats,
            "current_week": path.current_week,
            "completed_nodes": path.completed_nodes,
            "progress_percentage": path.progress_percentage,
            "created_at": path.created_at,
            "is_active": path.is_active == 1
        }
    }

@path_generation_router.post("/user/{user_id}/path/{path_id}/complete-node")
async def mark_node_complete(
    user_id: int, 
    path_id: int, 
    node_data: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """
    Mark a node as completed and update progress
    """
    path = db.query(UserLearningPath).filter(
        UserLearningPath.id == path_id,
        UserLearningPath.user_id == user_id
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    node_id = node_data.get('node_id')
    if not node_id:
        raise HTTPException(status_code=400, detail="Node ID is required")
    
    # Add node to completed list if not already there
    completed_nodes = path.completed_nodes or []
    if node_id not in completed_nodes:
        completed_nodes.append(node_id)
        path.completed_nodes = completed_nodes
        
        # Update progress percentage
        total_nodes = len(path.path_data) if path.path_data else 1
        path.progress_percentage = min(100, round((len(completed_nodes) / total_nodes) * 100))
        
        db.commit()
    
    return {
        "success": True,
        "message": f"Node {node_id} marked as completed",
        "progress_percentage": path.progress_percentage,
        "completed_nodes": path.completed_nodes
    }

@path_generation_router.get("/user/{user_id}/all-paths")
async def get_all_user_paths(user_id: int, db: Session = Depends(get_db)):
    """
    Get all learning paths for a user (active and inactive)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    paths = db.query(UserLearningPath).filter(
        UserLearningPath.user_id == user_id
    ).order_by(UserLearningPath.created_at.desc()).all()
    
    return {
        "success": True,
        "paths": [
            {
                "id": path.id,
                "title": path.title,
                "learner_type": path.learner_type,
                "learning_domain": path.learning_domain,
                "study_weeks": path.study_weeks,
                "progress_percentage": path.progress_percentage,
                "is_active": path.is_active == 1,
                "created_at": path.created_at,
                "stats": path.stats
            }
            for path in paths
        ]
    }