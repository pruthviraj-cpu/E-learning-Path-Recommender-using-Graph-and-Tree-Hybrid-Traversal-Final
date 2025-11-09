from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TopicBase(BaseModel):
    title: str
    type: str
    estimated_time: float
    load: str
    difficulty: int
    resources: Dict[str, Any]
    embedding: List[float]
    prerequisites: List[str]
    subtopics: List[str]

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int

    class Config:
        from_attributes = True

class Section(BaseModel):
    title: str
    content: Optional[str] = None

class ReadingMaterial(BaseModel):
    title: str
    link: Optional[str] = None
    content: Optional[str] = None

class Project(BaseModel):
    title: str
    description: Optional[str] = ""
    link: Optional[str] = None

class ModuleContent(BaseModel):
    video_url: Optional[str] = None
    sections: List[Any] = []
    reading_materials: list[ReadingMaterial]
    projects: List[Project] = []
    quizzes: List[str] = []
    long_videos: List[str] = []
    short_videos: List[str] = []

class ModuleResponse(BaseModel):
    id: str
    title: str
    content: ModuleContent
    skills: List[str] = []
    difficulty: str


def map_module_to_response(module) -> ModuleResponse:
    # module.resources is your JSONB column
    resources = module.resources or {}

    # Extract videos and quizzes from the resources JSON
    long_videos = resources.get("Long_videos", [])
    short_videos = resources.get("Short_videos", [])
    quizzes = resources.get("quizzes", [])

    # Sections
    sections = [Section(title=t, content="") for t in module.subtopics or []]

    # Reading materials
    reading_materials = []
    reading_links = resources.get("reading_material", [])
    for idx, title in enumerate(module.subtopics or []):
        link = reading_links[idx] if idx < len(reading_links) else None
        if not title:
            continue
        reading_materials.append(
            ReadingMaterial(title=title, link=link, content="")
        )

    # Projects
    projects = [Project(title=p, description="", link=None) for p in resources.get("projects", [])]

    return ModuleResponse(
        id=module.id,
        title=module.title,
        content=ModuleContent(
            long_videos=long_videos,
            short_videos=short_videos,
            reading_materials=reading_materials,
            projects=projects,
            quizzes=quizzes
        ),
        skills=getattr(module, "skills", []),
        difficulty=str(getattr(module, "difficulty", "0"))
    )