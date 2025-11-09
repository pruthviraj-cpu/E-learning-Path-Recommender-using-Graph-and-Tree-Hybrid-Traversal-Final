from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from models.database import Base

class QuizResult(Base):
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    num_questions = Column(Integer, nullable=False)
    difficulty_level = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)  # Percentage score
    correct_answers = Column(Integer, nullable=False)
    completion_status = Column(String(20), default="completed")
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    quiz_data = Column(JSON)  # Store complete quiz structure
    user_answers = Column(JSON)  # Store user's selections
    time_taken_seconds = Column(Integer)  # Time taken to complete
    confidence_rating = Column(Integer)  # 1-5 scale
    created_at = Column(DateTime(timezone=True), server_default=func.now())