from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.user_activity_models import UserActivity
from schemas.user_activity_schemas import UserActivityCreate, UserActivityResponse
from typing import List

user_activity_router = APIRouter(
    prefix="/activity", 
    tags=["User Activity"]
    )

@user_activity_router.post("/{user_id}/log", response_model=UserActivityResponse)
def log_activity(user_id: int, activity: UserActivityCreate, db: Session = Depends(get_db)):
    new_activity = UserActivity(user_id=user_id, **activity.dict())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@user_activity_router.get("/{user_id}", response_model=List[UserActivityResponse])
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    return db.query(UserActivity).filter(UserActivity.user_id == user_id).order_by(UserActivity.created_at.desc()).all()
