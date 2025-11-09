from models.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON, DateTime,func
from datetime import datetime
from sqlalchemy.orm import relationship
from models.user_activity_models import UserActivity

class User(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True)
    name=Column(String(100))
    password=Column(String(100))
    path = Column(JSON)
    learner_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    activities = relationship("UserActivity", back_populates="user", cascade="all, delete")