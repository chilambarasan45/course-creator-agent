from google.adk.agents import LlmAgent
from app.agents.adk_curriculum_agent import MODEL
from app.agents.prompts import QUIZ_AGENT_PROMPT

def get_quiz_agent():
    return LlmAgent(
        name="QuizAgent",
        model=MODEL,
        instruction=QUIZ_AGENT_PROMPT,
        description="Generates quiz questions from lesson content",
        output_key="quiz_result"
    )