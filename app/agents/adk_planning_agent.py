from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.prompts import PLANNING_AGENT_PROMPT

def get_planning_agent():
    return LlmAgent(
        name="PlanningAgent",
        model=MODEL,
        instruction=PLANNING_AGENT_PROMPT,
        description="Plans course structure and subtopics before research and curriculum",
        output_key="plan_result"
    )