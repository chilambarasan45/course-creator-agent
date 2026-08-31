from fastapi import FastAPI
from app.api.routes.course import router as course_router
from app.db.database import init_db

app = FastAPI(title="Course Creator Agent")

init_db()

app.include_router(course_router)


@app.get("/")
def root():
    return {"message": "Course Creator Agent API is running"}