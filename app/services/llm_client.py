import litellm
from app.core.config import GEMINI_API_KEY
import os

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


def ask_llm(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the text response.
    """
    response = litellm.completion(
        model="gemini/gemini-3.5-flash-lite",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content