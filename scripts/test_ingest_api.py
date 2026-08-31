import requests

url = "http://127.0.0.1:8000/ingest"

files = [
    ("files", open("data/source_docs/base paper.pdf", "rb")),
]

response = requests.post(url, files=files)
print(response.json())