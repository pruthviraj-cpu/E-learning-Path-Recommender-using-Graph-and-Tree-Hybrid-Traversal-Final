from fastapi import FastAPI
from routes.auth_routes import auth_router
from routes.path_routes import path_router
from routes.topic_routes import topic_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LearnerPath API")


app.include_router(auth_router)
app.include_router(path_router)
app.include_router(topic_router)

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # or ["http://localhost:3000"] for specific frontend
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