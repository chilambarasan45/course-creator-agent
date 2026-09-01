from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL,strip_reasoning_from_response
from app.agents.adk_tools import search_reference_material
from app.agents.prompts import CONTENT_WRITER_AGENT_PROMPT

def get_content_writer_agent():
    return LlmAgent(
        name="ContentWriterAgent",
        model=MODEL,
        instruction=CONTENT_WRITER_AGENT_PROMPT,
        description="Writes lesson content for each module, revising based on reviewer feedback",
        tools=[search_reference_material],
        output_key="content_result",
        after_model_callback=strip_reasoning_from_response
    )