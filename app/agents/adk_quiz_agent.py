from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL

quiz_agent = LlmAgent(
    name="QuizAgent",
    model=MODEL,
    instruction="""
    You are a Quiz Agent. Using the lesson content in 'content_result',
    create 3 multiple-choice questions per module to test understanding.
    Return ONLY a JSON array in this format:
    [{"question": "...", "options": ["A","B","C","D"], "correct_answer": "..."}]
    """,
    description="Generates quiz questions from lesson content",
    output_key="quiz_result"
)