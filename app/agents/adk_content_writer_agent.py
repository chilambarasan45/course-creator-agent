from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.adk_tools import make_search_reference_material
from app.agents.prompts import CONTENT_WRITER_AGENT_PROMPT

def get_content_writer_agent(source):
    return LlmAgent(
        name="ContentWriterAgent",
        model=MODEL,
        instruction=CONTENT_WRITER_AGENT_PROMPT,
        description="Writes lesson content for each module, revising based on reviewer feedback",
        tools=[make_search_reference_material(source)],
        output_key="content_result"
    )