from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
import json
from app.core.logger import get_logger
logger = get_logger("course_creator")

from app.agents.adk_planning_agent import get_planning_agent
from app.agents.adk_research_agent import get_research_agent
from app.agents.adk_curriculum_agent import get_curriculum_agent
from app.agents.adk_content_writer_agent import get_content_writer_agent
from app.agents.adk_reviewer_agent import get_reviewer_agent
from app.agents.adk_quiz_agent import get_quiz_agent
from app.rag.vector_store import get_all_source_chunks
from app.agents.adk_web_search_agent import get_web_search_agent
APP_NAME = "course_creator"

import litellm
litellm.suppress_debug_info = True
import asyncio
import re

_original_acompletion = litellm.acompletion


def _strip_reasoning(messages):
    if messages:
        for m in messages:
            if isinstance(m, dict):
                m.pop("reasoning_content", None)
                m.pop("reasoning", None)
    return messages


async def _patched_acompletion(*args, **kwargs):
    kwargs["messages"] = _strip_reasoning(kwargs.get("messages"))
    return await _original_acompletion(*args, **kwargs)


async def _patched_acompletion_with_retry(*args, **kwargs):
    max_retries = 10
    for attempt in range(max_retries):
        try:
            return await _patched_acompletion(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str and attempt < max_retries - 1:
                match = re.search(r"try again in ([\d.]+)s", error_str)
                wait_time = max(float(match.group(1)) + 2, 15)
                logger.warning(f"Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Non-retryable error: {error_str}")
                raise


litellm.acompletion = _patched_acompletion_with_retry


def _safe_json_loads(raw, default):
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


# --- Original: topic-typed course generation (unchanged) ---
async def run_adk_course_generation(topic: str, level: str, generate_quiz: bool = True) -> dict:
    logger.info(f"Starting course generation: topic='{topic}', level='{level}', quiz={generate_quiz}")

    session_service = InMemorySessionService()
    user_id = "api_user"
    session_id = f"session_{topic}_{level}_{uuid.uuid4()}"

    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    review_loop = LoopAgent(
        name="ContentReviewLoop",
        sub_agents=[get_content_writer_agent(source=None), get_reviewer_agent()],
        max_iterations=1
    )

    sub_agents = [get_planning_agent(), get_research_agent(source=None), get_curriculum_agent(), review_loop]
    if generate_quiz:
        sub_agents.append(get_quiz_agent())

    pipeline = SequentialAgent(
        name="CoursePipeline",
        sub_agents=sub_agents,
        description="Runs planning, research, curriculum, a content review loop, and optional quiz generation"
    )

    runner = Runner(agent=pipeline, app_name=APP_NAME, session_service=session_service)

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=f"Topic: {topic}, Level: {level}")]
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_message
            ):
            logger.debug(f"Event from {getattr(event, 'author', '?')}: {event}")
    except Exception as e:
        logger.error(f"Pipeline failed for topic='{topic}': {e}")
        raise

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    logger.info(f"Course generation complete for topic='{topic}'")

    return {
        "topic": topic,
        "level": level,
        "plan": _safe_json_loads(session.state.get("plan_result"), {}),
        "research": _safe_json_loads(session.state.get("research_result"), {}),
        "curriculum": _safe_json_loads(session.state.get("curriculum_result"), []),
        "content": session.state.get("content_result", ""),
        "review": session.state.get("review_result", ""),
        "quiz": _safe_json_loads(session.state.get("quiz_result"), []) if generate_quiz else None
    }


# --- New: curriculum from a selected document ---
async def run_adk_curriculum_for_document(filename: str) -> dict:
    logger.info(f"Starting curriculum generation for document='{filename}'")

    document_preview = get_all_source_chunks(source=filename, limit_chars=12000)

    session_service = InMemorySessionService()
    user_id = "api_user"
    session_id = f"session_doc_{filename}_{uuid.uuid4()}"

    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    pipeline = SequentialAgent(
        name="CurriculumPipeline",
        sub_agents=[get_planning_agent(), get_research_agent(source=filename), get_curriculum_agent()],
        description="Runs planning, document-scoped research, and curriculum generation"
    )

    runner = Runner(agent=pipeline, app_name=APP_NAME, session_service=session_service)

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=(
            f"Document: {filename}\n\n"
            f"Here is an excerpt of the actual document content:\n{document_preview}\n\n"
            "Base your subtopics ONLY on what is actually present in this excerpt. "
            "Analyze this document and identify the main topics and subtopics it covers, "
            "organized as a course curriculum."
        ))]
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_message
            ):
            logger.debug(f"Event from {getattr(event, 'author', '?')}: {event}")
    except Exception as e:
        logger.error(f"Curriculum pipeline failed for document='{filename}': {e}")
        raise

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    logger.info(f"Curriculum generation complete for document='{filename}'")

    return {
        "filename": filename,
        "curriculum": _safe_json_loads(session.state.get("curriculum_result"), [])
    }

# --- New: content + review loop + quiz for one selected subtopic ---


async def run_adk_topic_pipeline(filename: str, topic_title: str, generate_quiz: bool = True) -> dict:
    logger.info(f"Starting topic content generation: document='{filename}', topic='{topic_title}'")

    session_service = InMemorySessionService()
    user_id = "api_user"
    session_id = f"session_topic_{filename}_{uuid.uuid4()}"

    initial_curriculum = json.dumps([{"title": topic_title, "description": ""}])

    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id,
        state={"curriculum_result": initial_curriculum}
    )

    review_loop = LoopAgent(
        name="ContentReviewLoop",
        sub_agents=[get_content_writer_agent(source=filename), get_reviewer_agent()],
        max_iterations=2
    )

    sub_agents = [get_web_search_agent(source=filename), review_loop]
    if generate_quiz:
        sub_agents.append(get_quiz_agent())

    pipeline = SequentialAgent(
        name="TopicPipeline",
        sub_agents=sub_agents,
        description="Searches document and web, writes and reviews content, then optionally generates a quiz"
    )

    runner = Runner(agent=pipeline, app_name=APP_NAME, session_service=session_service)

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=f"Topic: {topic_title}")]
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_message
            ):
            logger.debug(f"Event from {getattr(event, 'author', '?')}: {event}")
    except Exception as e:
        logger.error(f"Topic pipeline failed for topic='{topic_title}': {e}")
        raise

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    logger.info(f"Topic content generation complete for topic='{topic_title}'")

    return {
        "topic": topic_title,
        "content": session.state.get("content_result", ""),
        "review": session.state.get("review_result", ""),
        "quiz": _safe_json_loads(session.state.get("quiz_result"), []) if generate_quiz else None
    }