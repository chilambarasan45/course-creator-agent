from pydantic import BaseModel


class CourseRequest(BaseModel):
    topic: str
    level: str