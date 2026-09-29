import chromadb

from app.rag.embeddings import embed_chunks

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="course_documents")


def get_collection():
    """Returns the ChromaDB collection so other files can use it."""
    return collection


def store_chunks(chunks: list[str], embeddings: list[list[float]], source_file: str = None, course_id: int = None):
    """
    Stores chunks. Pass source_file for ingested reference docs,
    or course_id for generated course content — not both.
    """
    prefix = source_file if source_file else f"course_{course_id}"
    ids = [f"{prefix}_chunk_{i}" for i in range(len(chunks))]

    if course_id is not None:
        metadatas = [{"course_id": course_id} for _ in chunks]
    else:
        metadatas = [{"source": source_file} for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )





def query_chunks(query_text: str, n_results: int = 3):
    query_embedding = embed_chunks([query_text])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    chunks_with_source = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks_with_source.append({"text": doc, "source": meta.get("source")})

    return chunks_with_source



def semantic_search(query_text: str, n_results: int = 5, course_id: int = None, source: str = None) -> list[dict]:
    query_embedding = embed_chunks([query_text])
    where = None
    if course_id is not None:
        where = {"course_id": course_id}
    elif source is not None:
        where = {"source": source}

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where=where
    )

    return [{"id": doc_id, "text": doc}
            for doc_id, doc in zip(results["ids"][0], results["documents"][0])]


def get_all_source_chunks(source: str, limit_chars=15000):
    """Returns concatenated text from a single ingested source document."""
    data = collection.get(where={"source": source})
    texts = []
    total = 0
    for doc in data["documents"]:
        texts.append(doc)
        total += len(doc)
        if total > limit_chars:
            break
    return "\n\n".join(texts)