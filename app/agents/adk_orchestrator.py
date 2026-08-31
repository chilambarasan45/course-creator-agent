from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

from app.agents.adk_planning_agent import planning_agent
from app.agents.adk_research_agent import research_agent
from app.agents.adk_curriculum_agent import curriculum_agent
from app.agents.adk_content_writer_agent import content_writer_agent
from app.agents.adk_reviewer_agent import reviewer_agent
from app.agents.adk_quiz_agent import quiz_agent

review_loop = LoopAgent(
    name="ContentReviewLoop",
    sub_agents=[content_writer_agent, reviewer_agent],
    max_iterations=3
)

course_pipeline = SequentialAgent(
    name="CoursePipeline",
    sub_agents=[planning_agent, research_agent, curriculum_agent, review_loop, quiz_agent],
    description="Runs planning, research, curriculum, a content review loop, and quiz generation"
)

APP_NAME = "course_creator"


async def run_adk_course_generation(topic: str, level: str, generate_quiz: bool = True) -> dict:
    session_service = InMemorySessionService()
    user_id = "api_user"
    session_id = f"session_{topic}_{level}"

    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    sub_agents = [planning_agent, research_agent, curriculum_agent, review_loop]
    if generate_quiz:
        sub_agents.append(quiz_agent)

    pipeline = SequentialAgent(
        name="CoursePipeline",
        sub_agents=sub_agents,
        description="Runs planning, research, curriculum, review loop, and optional quiz"
    )

    runner = Runner(
        agent=pipeline,
        app_name=APP_NAME,
        session_service=session_service
    )

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

    course = {
        "topic": topic,
        "level": level,
        "plan": session.state.get("plan_result", "{}"),
        "research": session.state.get("research_result", "{}"),
        "curriculum": session.state.get("curriculum_result", "[]"),
        "content": session.state.get("content_result", ""),
        "review": session.state.get("review_result", ""),
        "quiz": session.state.get("quiz_result", "[]") if generate_quiz else None
    }
    return course