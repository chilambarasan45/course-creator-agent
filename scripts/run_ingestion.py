from app.rag.ingestion import ingest_folder

ingest_folder("data/source_docs")

print("Ingestion complete.")