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

    