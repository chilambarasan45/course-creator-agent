import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOGS_PATH = os.getenv("LOGS_PATH", "logs")