from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from models.database import Base

class UserLearningPath(Base):
    __tablename__ = "user_learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # User preferences
    learner_type = Column(String(50), nullable=False)  # beginner, intermediate, etc.
    time_availability = Column(String(50), nullable=False)  # part_time, full_time, etc.
    learning_domain = Column(String(50), nullable=False)  # ai_ml, web_dev, etc.
    study_weeks = Column(Integer, nullable=False, default=12)
    
    # Path data (store the complete path structure)
    path_data = Column(JSON, nullable=False)  # Complete path structure
    weekly_schedule = Column(JSON, nullable=False)  # Weekly breakdown
    stats = Column(JSON, nullable=False)  # Statistics about the path
    
    # Progress tracking
    current_week = Column(Integer, default=1)
    completed_nodes = Column(JSON, default=[])  # List of completed node IDs
    progress_percentage = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive