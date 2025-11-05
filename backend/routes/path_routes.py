from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.path_models import Path
from schemas.paths_schemas import PathCreate, PathResponse
from models.database import get_db

path_router = APIRouter(
    prefix="/paths",
    tags=["Paths"]
)

@path_router.post("/", response_model=PathResponse)
def create_path(path: PathCreate, db: Session = Depends(get_db)):
    new_path = Path(**path.dict())
    db.add(new_path)
    db.commit()
    db.refresh(new_path)
    return new_path

@path_router.get("/", response_model=list[PathResponse])
def get_all_paths(db: Session = Depends(get_db)):
    paths = db.query(Path).all()
    return paths

@path_router.get("/{path_id}", response_model=PathResponse)
def get_path(path_id: int, db: Session = Depends(get_db)):
    path = db.query(Path).filter(Path.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    return path