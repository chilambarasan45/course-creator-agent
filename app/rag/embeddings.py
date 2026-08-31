from sentence_transformers import SentenceTransformer

# Load the embedding model once (reused across the app)
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Converts a list of text chunks into embedding vectors.

    Args:
        chunks: list of text chunks

    Returns:
        list of embedding vectors (one per chunk)
    """
    embeddings = model.encode(chunks).tolist()
    return embeddings