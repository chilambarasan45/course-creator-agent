import litellm
from app.rag.vector_store import semantic_search
from app.rag.keyword_search import keyword_search
from app.rag.fusion import reciprocal_rank_fusion
from app.agents.prompts import QA_AGENT_PROMPT

from app.core.logger import get_logger
logger = get_logger(__name__)

NO_INFO_MSG = "There is no information about this in the uploaded document."


async def answer_question(question: str) -> dict:
    semantic_results = semantic_search(question, n_results=8)
    keyword_results = keyword_search(question, n_results=8)
    fused = reciprocal_rank_fusion([semantic_results, keyword_results])
    top_chunks = fused[:6]

    logger.info(f"Question: {question}")
    logger.info(f"Retrieved {len(top_chunks)} chunks:")
    for c in top_chunks:
        logger.info(f"  - source={c['source']} score={c['score']:.4f} text_preview={c['text'][:80]!r}")

    if not top_chunks:
        context = "No relevant material found in the document."
    else:
        context = "\n\n".join([chunk["text"] for chunk in top_chunks])

    prompt = QA_AGENT_PROMPT.format(context=context, question=question)

    response = await litellm.acompletion(
        model="gemini/gemini-3.5-flash-lite",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    answer = response.choices[0].message.content

    sources = []
    if answer.strip() != NO_INFO_MSG and top_chunks:
        sources = list({chunk["source"] for chunk in top_chunks})

    return {"answer": answer, "sources": sources}