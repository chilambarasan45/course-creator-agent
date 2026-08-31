from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.adk_tools import exit_loop

reviewer_agent = LlmAgent(
    name="ReviewerAgent",
    model=MODEL,
    instruction="""
    You are a Reviewer Agent. Review the lesson content in 'content_result'.

    Check for: clarity, correctness, beginner-friendliness, and whether it
    matches the module descriptions in 'curriculum_result'.

    If the content is good, call the exit_loop tool to approve it and stop.
    If it needs work, respond with exactly: REVISE: <specific feedback>
    (do NOT call exit_loop in that case)
    """,
    description="Reviews lesson content and either approves (exits loop) or requests revision",
    tools=[exit_loop],
    output_key="review_result"
)