from sqlalchemy import Column, Integer, String, Float, JSON,ARRAY
from models.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    # description = Column(String)
    type = Column(String)
    estimated_time = Column(Integer)
    load = Column(String)
    difficulty = Column(Integer)
    prerequisites = Column(ARRAY(String))
    subtopics = Column(ARRAY(String))
    resources = Column(JSON)