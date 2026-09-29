from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os

from app.models.schemas import (
    CourseRequest, CourseResponse,
    AskRequest, AskResponse,
    ModuleRequest, ModuleResponse
)
from app.agents.adk_orchestrator import (
    run_adk_course_generation,
    run_adk_curriculum_for_document,
    run_adk_topic_pipeline
)
from app.services.llm_client import ask_llm
from app.agents.prompts import ASK_PROMPT
from app.rag.ingestion import ingest_document
from app.rag.vector_store import semantic_search
from app.rag.keyword_search import keyword_search
from app.rag.fusion import reciprocal_rank_fusion
from app.db.database import (
    save_course, get_course,
    save_subtopic_content, get_subtopic_content,
    save_full_course, list_saved_courses
)

router = APIRouter()

SOURCE_DIR = "data/source_docs"


class SaveCourseRequest(BaseModel):
    curriculum: list[dict]  # [{title, subtopics: [str, ...]}]


# --- Documents ---
@router.get("/documents")
def list_documents():
    if not os.path.exists(SOURCE_DIR):
        return []
    return [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]


# --- Curriculum for a document (agentic: Planning -> Research -> Curriculum) ---
@router.get("/document/{filename}/curriculum")
async def get_curriculum_for_document(filename: str):
    return await run_adk_curriculum_for_document(filename)


# --- Topic content for a subtopic (agentic: ContentWriter <-> Reviewer loop -> Quiz), cached ---
@router.post("/document/{filename}/topic", response_model=ModuleResponse)
async def get_topic_content(filename: str, request: ModuleRequest):
    cached = get_subtopic_content(filename, request.module_title)
    if cached:
        return cached

    result = await run_adk_topic_pipeline(filename, request.module_title, generate_quiz=True)

    save_subtopic_content(
        filename, request.module_title,
        result.get("content", ""), result.get("review", ""), result.get("quiz") or []
    )

    return {
        "content": result.get("content", ""),
        "quiz": result.get("quiz") or []
    }


# --- Save a document's generated course (uses already-cached subtopic content) ---
@router.post("/document/{filename}/save-course")
def save_course_for_document(filename: str, request: SaveCourseRequest):
    full_data = {"filename": filename, "curriculum": []}
    for topic in request.curriculum:
        topic_entry = {"title": topic["title"], "subtopics": []}
        for sub in topic.get("subtopics", []):
            cached = get_subtopic_content(filename, sub)
            topic_entry["subtopics"].append({
                "title": sub,
                "content": cached["content"] if cached else None,
                "quiz": cached["quiz"] if cached else []
            })
        full_data["curriculum"].append(topic_entry)

    course_id = save_full_course(filename, full_data)
    return {"course_id": course_id, "filename": filename}


# --- Saved courses ---
@router.get("/courses")
def get_saved_courses():
    return list_saved_courses()


@router.get("/courses/{course_id}")
def get_saved_course(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Saved course not found")
    return course


# --- Chatbot, scoped to selected document ---
@router.post("/ask", response_model=AskResponse)
def ask_document(request: AskRequest):
    sem = semantic_search(request.question, source=request.filename)
    kw = keyword_search(request.question, source=request.filename)
    chunks = reciprocal_rank_fusion([sem, kw])[:5]
    context = "\n\n".join(c["text"] for c in chunks)

    if not context.strip():
        return AskResponse(answer="There is no information on this in the generated document.")

    answer = ask_llm(ASK_PROMPT.format(context=context, question=request.question))
    return AskResponse(answer=answer)


# --- Original topic-typed course generation (kept, not wired to current UI) ---
@router.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest):
    result = await run_adk_course_generation(
        request.topic, request.level, request.generate_quiz
    )
    course_id = save_course(request.topic, request.level, result)
    result["course_id"] = course_id
    return result


# --- Ingest new documents ---
@router.post("/ingest")
async def ingest_documents(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        save_path = os.path.join(SOURCE_DIR, file.filename)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        num_chunks = ingest_document(save_path)
        results.append({"filename": file.filename, "chunks": num_chunks})
    return {"ingested": results}