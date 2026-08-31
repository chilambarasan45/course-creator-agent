import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.adk_orchestrator import course_pipeline

APP_NAME = "course_creator"
USER_ID = "test_user"
SESSION_ID = "test_session"


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=course_pipeline,
        app_name=APP_NAME,
        session_service=session_service
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text="Topic: Python, Level: beginner")]
    )

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_message
    ):
        if event.is_final_response():
            print(f"\n--- {event.author} ---")
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())