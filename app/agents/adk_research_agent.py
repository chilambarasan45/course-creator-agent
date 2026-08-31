from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.adk_tools import search_reference_material

research_agent = LlmAgent(
    name="ResearchAgent",
    model=MODEL,
    instruction="""
    You are a Research Agent. Using the subtopics in 'plan_result',
    call the search_reference_material tool once per subtopic to gather
    real reference material.

    Compile the findings into organized research notes per subtopic.
    Return ONLY a JSON object mapping each subtopic to its research notes.
    """,
    description="Gathers reference material per subtopic using hybrid search",
    tools=[search_reference_material],
    output_key="research_result"
)