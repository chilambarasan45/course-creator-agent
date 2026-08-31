from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.core.config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


MODEL = LiteLlm(model="groq/openai/gpt-oss-120b")

curriculum_agent = LlmAgent(
    name="CurriculumAgent",
    model=MODEL,
    instruction="""
    You are a Curriculum Agent. Using the subtopics and notes in 'plan_result',
    and the reference material in 'research_result', create a course curriculum.

    Base your modules on the planned subtopics, and ground each module's
    description in the corresponding research notes where available.

    Return ONLY a JSON array in this format:
    [{"title": "Module title", "description": "short description"}, ...]

    Generate one module per subtopic from the plan (4-6 modules).
    """,
    description="Generates course curriculum modules grounded in the plan and research",
    output_key="curriculum_result"
)