# check_chunks.py (put in project root)
from app.rag.vector_store import get_collection

collection = get_collection()
data = collection.get()

for cid, doc, meta in zip(data["ids"], data["documents"], data["metadatas"]):
    print("ID:", cid)
    print("SOURCE:", meta.get("source"))
    print("TEXT:", doc[:300])  # first 300 chars
    print("-" * 50)