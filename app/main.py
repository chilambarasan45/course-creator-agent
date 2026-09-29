from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes.course import router as course_router
from app.db.database import init_db

app = FastAPI(title="Course Creator Agent")

init_db()

app.include_router(course_router)

app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


@app.get("/")
def root():
    return {"message": "Course Creator Agent API is running"}