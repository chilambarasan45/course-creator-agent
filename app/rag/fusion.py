def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = 60) -> list[dict]:
    scores = {}
    texts = {}
    sources = {}

    for results in result_lists:
        for rank, item in enumerate(results):
            doc_id = item["id"]
            texts[doc_id] = item["text"]
            sources[doc_id] = item.get("source", "unknown")
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"id": doc_id, "text": texts[doc_id], "source": sources[doc_id], "score": score} for doc_id, score in fused]