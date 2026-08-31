import re
import math
from app.rag.vector_store import get_collection

STOPWORDS = {"the", "a", "an", "is", "on", "and", "are", "of", "in", "to", "for", "with"}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS]
    return words


def build_tfidf_scores(query: str, chunks: dict[str, str]) -> dict[str, float]:
    """
    chunks = {chunk_id: chunk_text}. Builds TF-IDF using ONLY these chunks
    as the corpus.
    """
    total_docs = len(chunks)
    query_tokens = tokenize(query)

    chunk_tokens = {cid: tokenize(text) for cid, text in chunks.items()}

    scores = {cid: 0.0 for cid in chunks}

    for word in query_tokens:
        docs_with_word = [cid for cid, tokens in chunk_tokens.items() if word in tokens]
        if not docs_with_word:
            continue

        idf = math.log(total_docs / len(docs_with_word)) if len(docs_with_word) < total_docs else 0.01

        for cid in docs_with_word:
            tokens = chunk_tokens[cid]
            tf = tokens.count(word) / len(tokens) if tokens else 0
            scores[cid] += tf * idf

    return scores


def keyword_search(query: str, n_results: int = 5) -> list[dict]:
    collection = get_collection()
    data = collection.get()

    chunks = {cid: text for cid, text in zip(data["ids"], data["documents"])}

    scores = build_tfidf_scores(query, chunks)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top = ranked[:n_results]

    return [{"id": cid, "text": chunks[cid]} for cid, score in top if score > 0]