from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os

from app.models.schemas import CourseRequest, CourseResponse
from app.agents.adk_orchestrator import run_adk_course_generation
from app.rag.ingestion import ingest_document
from app.db.database import save_course, get_course

router = APIRouter()


@router.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest):
    result = await run_adk_course_generation(
        request.topic, request.level, request.generate_quiz
    )
    course_id = save_course(request.topic, request.level, result)
    result["course_id"] = course_id
    return result


@router.get("/course/{course_id}", response_model=CourseResponse)
def fetch_course(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/ingest")
async def ingest_documents(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        save_path = os.path.join("data/source_docs", file.filename)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        num_chunks = ingest_document(save_path)
        results.append({"filename": file.filename, "chunks": num_chunks})
    return {"ingested": results}