from groq import Groq
from app.core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def ask_llm(prompt: str) -> str:
    """
    Sends a prompt to the LLM (via Groq) and returns the text response.
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content