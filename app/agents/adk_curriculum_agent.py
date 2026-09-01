from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.core.config import GROQ_API_KEY
from app.agents.prompts import CURRICULUM_AGENT_PROMPT
import os


os.environ["GROQ_API_KEY"] = GROQ_API_KEY
MODEL = LiteLlm(
    model="groq/openai/gpt-oss-20b",
    additional_drop_params=["reasoning_content"],
    max_tokens=1200,
    timeout=30
)
def strip_reasoning_from_response(callback_context, llm_response):
    """
    Removes 'thought' parts from the model's response immediately after
    generation, before ADK stores them in session history. This prevents
    ADK from replaying reasoning content in the next turn, which Groq
    rejects (known ADK bug: google/adk-python#3948).
    """
    if llm_response and llm_response.content and llm_response.content.parts:
        cleaned_parts = [
            p for p in llm_response.content.parts
            if not getattr(p, "thought", False)
        ]
        llm_response.content.parts = cleaned_parts
    return None

def get_curriculum_agent():
    return LlmAgent(
        name="CurriculumAgent",
        model=MODEL,
        instruction=CURRICULUM_AGENT_PROMPT,
        description="Generates course curriculum modules grounded in the plan and research",
        output_key="curriculum_result"
    )