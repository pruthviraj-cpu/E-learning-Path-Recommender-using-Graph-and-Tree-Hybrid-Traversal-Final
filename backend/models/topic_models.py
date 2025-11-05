from sqlalchemy import Column, Integer, String, Float, JSON
from models.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    type = Column(String(50))
    estimated_time = Column(Float)
    load = Column(String(50))
    difficulty = Column(Integer)
    resources = Column(JSON)
    embedding = Column(JSON)
    prerequisites = Column(JSON)
    subtopics = Column(JSON)