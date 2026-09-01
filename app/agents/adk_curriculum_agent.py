from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.core.config import GROQ_API_KEY
import os
from app.agents.prompts import CURRICULUM_AGENT_PROMPT
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


MODEL = LiteLlm(model="groq/llama-3.3-70b-versatile")

curriculum_agent = LlmAgent(
    name="CurriculumAgent",
    model=MODEL,
    instruction=CURRICULUM_AGENT_PROMPT,
    description="Generates course curriculum modules grounded in the plan and research",
    output_key="curriculum_result"
)



