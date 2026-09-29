from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.adk_tools import make_search_reference_material
from app.agents.prompts import RESEARCH_AGENT_PROMPT

def get_research_agent(source):
    return LlmAgent(
        name="ResearchAgent",
        model=MODEL,
        instruction=RESEARCH_AGENT_PROMPT,
        description="Gathers reference material per subtopic using hybrid search",
        tools=[make_search_reference_material(source)],
        output_key="research_result"
    )