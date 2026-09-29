import os
import fitz  # pymupdf
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_chunks
from app.rag.vector_store import store_chunks


def read_pdf(file_path: str) -> str:
    """Extracts all text from a PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def ingest_document(file_path: str):
    if file_path.endswith(".pdf"):
        text = read_pdf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    filename = os.path.basename(file_path)

    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    store_chunks(chunks, embeddings, source_file=filename)

    print(f"Ingested {len(chunks)} chunks from {filename}")
    return len(chunks) 


def ingest_folder(folder_path: str):
    """
    Ingests all PDF and TXT files inside a folder.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf") or filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            ingest_document(file_path)

