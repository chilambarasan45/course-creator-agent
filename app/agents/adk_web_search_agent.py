from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.adk_tools import make_search_reference_material, web_search
from app.agents.prompts import WEB_SEARCH_AGENT_PROMPT

def get_web_search_agent(source):
    return LlmAgent(
        name="WebSearchAgent",
        model=MODEL,
        instruction=WEB_SEARCH_AGENT_PROMPT,
        description="Searches the document first, then supplements with web search if the document material is thin",
        tools=[make_search_reference_material(source), web_search],
        output_key="web_research_result"
    )