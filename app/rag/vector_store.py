import chromadb

from app.rag.embeddings import embed_chunks

# Create a persistent ChromaDB client (saves data to disk, not just memory)
client = chromadb.PersistentClient(path="./chroma_data")

# Get or create a collection (like a "table" for our course documents)
collection = client.get_or_create_collection(name="course_documents")


def get_collection():
    """Returns the ChromaDB collection so other files can use it."""
    return collection

def store_chunks(chunks: list[str], embeddings: list[list[float]], source_file: str):
    """
    Stores text chunks, their embeddings, and source file info into ChromaDB.
    """
    ids = [f"{source_file}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source_file} for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
def semantic_search(query_text: str, n_results: int = 5) -> list[dict]:
    query_embedding = embed_chunks([query_text])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    return [{"id": doc_id, "text": doc}
            for doc_id, doc in zip(results["ids"][0], results["documents"][0])]

def query_chunks(query_text: str, n_results: int = 3):
    query_embedding = embed_chunks([query_text])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    chunks_with_source = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks_with_source.append({"text": doc, "source": meta["source"]})

    return chunks_with_source