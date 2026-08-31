from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.adk_tools import search_reference_material

content_writer_agent = LlmAgent(
    name="ContentWriterAgent",
    model=MODEL,
    instruction="""
    You are a Content Writer Agent. Using the curriculum in 'curriculum_result',
    write a clear, beginner-friendly lesson for each module.

    Before writing each module's content, use the search_reference_material tool
    with the module title to find relevant source material. Ground your lesson
    in that material — do not just copy it, rewrite it clearly for a learner.

    If 'review_result' exists and starts with "REVISE:", fix the specific issues
    mentioned there in your next draft.

    Structure each lesson with an introduction, explanations with examples,
    and a summary.
    """,
    description="Writes lesson content for each module, revising based on reviewer feedback",
    tools=[search_reference_material],
    output_key="content_result"
)