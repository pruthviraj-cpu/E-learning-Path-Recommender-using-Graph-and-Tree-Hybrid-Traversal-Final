from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.topic_models import Topic
from schemas.topic_schemas import TopicCreate, TopicResponse
from models.database import get_db

topic_router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)

@topic_router.post("/", response_model=TopicResponse)
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    new_topic = Topic(**topic.dict())
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic

@topic_router.get("/", response_model=list[TopicResponse])
def get_all_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return topics

@topic_router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
