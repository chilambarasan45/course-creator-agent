from app.rag.vector_store import semantic_search
from app.rag.keyword_search import keyword_search
from app.rag.fusion import reciprocal_rank_fusion

from google.adk.tools import ToolContext

def exit_loop(tool_context: ToolContext):
    """Call this tool when the content has been approved, to stop the review loop."""
    tool_context.actions.escalate = True
    return {"status": "loop exited"}


def search_reference_material(module_title: str) -> str:
    """
    Searches the knowledge base for reference material relevant to a given module title.
    Uses hybrid search (semantic + keyword) combined via RRF.
    """
    semantic_results = semantic_search(module_title, n_results=5)
    keyword_results = keyword_search(module_title, n_results=5)

    fused = reciprocal_rank_fusion([semantic_results, keyword_results])
    top_chunks = fused[:3]

    if not top_chunks:
        return "No reference material found for this topic."

    return "\n\n".join([chunk["text"] for chunk in top_chunks])