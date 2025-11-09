from fastapi import FastAPI
from routes.auth_routes import auth_router
from routes.path_routes import path_router
from routes.topic_routes import topic_router
from routes.path_generation_routes import path_generation_router
from routes.learning_paths_routes import learning_paths_router
from routes.path_generation_routes import path_generation_router
from routes.user_activity_routes import user_activity_router
from routes.onboarding_quiz_routes import onboarding_quiz_router
from routes.learner_type_quiz_routes import learner_quiz_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="LearnerPath API")


app.include_router(auth_router)
app.include_router(path_router)
app.include_router(topic_router)
app.include_router(path_generation_router)
app.include_router(user_activity_router)
app.include_router(learning_paths_router)
app.include_router(path_generation_router)
app.include_router(onboarding_quiz_router)
app.include_router(learner_quiz_router)

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # or ["http://localhost:3000"] for specific frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return{"message": "Welcome to LearnerPath API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)