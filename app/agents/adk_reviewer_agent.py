from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL,strip_reasoning_from_response
from app.agents.adk_tools import exit_loop
from app.agents.prompts import REVIEWER_AGENT_PROMPT

def get_reviewer_agent():
    return LlmAgent(
        name="ReviewerAgent",
        model=MODEL,
        instruction=REVIEWER_AGENT_PROMPT,
        description="Reviews lesson content and either approves (exits loop) or requests revision",
        tools=[exit_loop],
        output_key="review_result",
        after_model_callback=strip_reasoning_from_response
    )