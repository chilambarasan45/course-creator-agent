from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL

planning_agent = LlmAgent(
    name="PlanningAgent",
    model=MODEL,
    instruction="""
    You are a Planning Agent. Given a topic and difficulty level,
    decide the course structure before any content is written.

    Return ONLY a JSON object in this format:
    {
        "subtopics": ["subtopic 1", "subtopic 2", ...],
        "notes": "any guidance on depth, order, or focus for this level"
    }

    Generate 4-6 subtopics appropriate for the given level.
    """,
    description="Plans course structure and subtopics before research and curriculum",
    output_key="plan_result"
)