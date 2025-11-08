from fastapi import APIRouter,Depends, HTTPException
from typing import List
from datetime import datetime
from schemas.user_schemas import LoginCredentials
from models.user_models import User
from models.path_models import Path
from sqlalchemy.orm import Session
from models.database import get_db

from fastapi.encoders import jsonable_encoder

auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth Routes']
)

@auth_router.post("/")
def login():
    
    return {"message": "Hello world!!!"}

# @auth_router.post("/login")
# def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.name == credentials.name).first()

#     if not user:
#         return {"success": False, "message": "User not found"}

#     if user.password != credentials.password:
#         return {"success": False, "message": "Incorrect password"}

#     user.last_login = datetime.utcnow()
#     db.commit()
#     db.refresh(user)

#     return {
#         "success": True,
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "path":user.path,
#         }
#     }

# import json

# @auth_router.post("/login")
# def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.name == credentials.name).first()

#     if not user:
#         return {"success": False, "message": "User not found"}

#     if user.password != credentials.password:
#         return {"success": False, "message": "Incorrect password"}

#     user.last_login = datetime.utcnow()
#     db.commit()
#     db.refresh(user)

#     path_value = None
#     if user.path:
#         if isinstance(user.path, str):
#             # If stored as JSON string
#             path_value = json.loads(user.path)
#         else:
#             # Already dict/list
#             path_value = user.path

#     return {
#         "success": True,
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "path": path_value
#         }
#     }


@auth_router.post("/login")
def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == credentials.name).first()

    if not user:
        return {"success": False, "message": "User not found"}

    if user.password != credentials.password:
        return {"success": False, "message": "Incorrect password"}

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    try:
        safe_path = jsonable_encoder(user.path)
    except Exception:
        safe_path = str(user.path)  

    response = {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "path": safe_path,
        },
    }

    return jsonable_encoder(response)
@auth_router.get("/enrolled/{user_id}", response_model=List[dict])
def get_enrolled_paths(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # user.path should be list of integers like [2, 4]
    path_ids = user.path or []
    if not path_ids:
        return []

    paths = db.query(Path).filter(Path.id.in_(path_ids)).all()
    return [
        {
            "id": p.id,
            "name": p.title,  # ✅ Use 'title' instead of 'name'
            "description": f"{p.type} path - {p.load} load",  # Create description
            "difficulty": p.difficulty,
            "topics": p.subnodes or [],  # Use subnodes as topics
            "is_active": p.id in path_ids
        }
        for p in paths
    ]

@auth_router.post("/signup")
async def registyer_user(credentials: LoginCredentials, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.name == credentials.name).first()

    if existing_user:
        return {"success": False, "message": "User already exists"}
    
    new_user = User(
        name=credentials.name,
        password=credentials.password,
        created_at=datetime.now()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response = {
        "success" :True,
        "user": {
            "id":new_user.id,
            "name":new_user.name,
            "created_at":new_user.created_at,
        }
    }
    return response