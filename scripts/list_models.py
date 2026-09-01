import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from app.core.config import GROQ_API_KEY

print("Using key:", GROQ_API_KEY[:10] + "..." if GROQ_API_KEY else "NO KEY FOUND")

resp = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
)

print("Status code:", resp.status_code)
print("Response:", resp.text)