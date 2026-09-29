from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.core.config import GEMINI_API_KEY
from app.agents.prompts import CURRICULUM_AGENT_PROMPT
import os


os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
MODEL = LiteLlm(
    model="gemini/gemini-3.5-flash-lite",
    max_tokens=12000,
    timeout=60
)

def get_curriculum_agent():
    return LlmAgent(
        name="CurriculumAgent",
        model=MODEL,
        instruction=CURRICULUM_AGENT_PROMPT,
        description="Generates course curriculum modules grounded in the plan and research",
        output_key="curriculum_result"
    )