from pydantic import BaseModel

class CourseRequest(BaseModel):
    topic: str
    level: str
    generate_quiz: bool = False

class CourseResponse(BaseModel):
    course_id: int
    topic: str
    level: str
    plan: dict
    research: dict
    curriculum: list[dict]
    content: str
    review: str
    quiz: list[dict] | None

class AskRequest(BaseModel):
    question: str
    filename: str

class AskResponse(BaseModel):
    answer: str

class ModuleRequest(BaseModel):
    module_title: str
    filename: str

class ModuleResponse(BaseModel):
    content: str
    quiz: list[dict]