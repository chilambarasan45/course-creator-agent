from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
import json

from app.agents.adk_planning_agent import get_planning_agent
from app.agents.adk_research_agent import get_research_agent
from app.agents.adk_curriculum_agent import get_curriculum_agent
from app.agents.adk_content_writer_agent import get_content_writer_agent
from app.agents.adk_reviewer_agent import get_reviewer_agent
from app.agents.adk_quiz_agent import get_quiz_agent

APP_NAME = "course_creator"

import litellm
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
    kwargs["messages"] = _trim_messages(kwargs["messages"], max_messages=6)
    return await _original_acompletion(*args, **kwargs)

async def _patched_acompletion_with_retry(*args, **kwargs):
    max_retries = 2
    for attempt in range(max_retries):
        try:
            return await _patched_acompletion(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str and attempt < max_retries - 1:
                match = re.search(r"try again in ([\d.]+)s", error_str)
                wait_time = float(match.group(1)) + 1 if match else 5
                print(f"Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                await asyncio.sleep(wait_time)
            else:
                raise


litellm.acompletion = _patched_acompletion_with_retry

def _trim_messages(messages, max_messages=8):
    """Keep system/first message, all user messages, and recent context."""
    if not messages or len(messages) <= max_messages:
        return messages

    first_msg = messages[0]
    user_messages = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]
    recent = messages[-(max_messages - 1):]

    # Ensure at least one user message survives
    if not any(isinstance(m, dict) and m.get("role") == "user" for m in recent):
        if user_messages:
            recent = [user_messages[-1]] + recent[1:]

    result = [first_msg] + recent if first_msg not in recent else recent
    return result


async def run_adk_course_generation(topic: str, level: str, generate_quiz: bool = True) -> dict:
    session_service = InMemorySessionService()
    user_id = "api_user"
    session_id = f"session_{topic}_{level}_{uuid.uuid4()}"

    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    review_loop = LoopAgent(
        name="ContentReviewLoop",
        sub_agents=[get_content_writer_agent(), get_reviewer_agent()],
        max_iterations=1
    )

    sub_agents = [get_planning_agent(), get_research_agent(), get_curriculum_agent(), review_loop]
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

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=user_message
    ):
        pass

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

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