from app.rag.vector_store import semantic_search
from app.rag.keyword_search import keyword_search
from app.rag.fusion import reciprocal_rank_fusion

from google.adk.tools import ToolContext
from duckduckgo_search import DDGS

def exit_loop(tool_context: ToolContext):
    """Call this tool when the content has been approved, to stop the review loop."""
    tool_context.actions.escalate = True
    return {"status": "loop exited"}


def make_search_reference_material(source: str):
    def search_reference_material(module_titles: list[str]) -> str:
        results = {}
        for title in module_titles:
            semantic_results = semantic_search(title, source=source, n_results=10)
            keyword_results = keyword_search(title, source=source, n_results=10)
            fused = reciprocal_rank_fusion([semantic_results, keyword_results])
            top_chunks = fused[:6]
            results[title] = "\n\n".join([chunk["text"] for chunk in top_chunks]) if top_chunks else "No reference material found."
        return "\n\n---\n\n".join([f"[{title}]\n{text}" for title, text in results.items()])
    return search_reference_material



def web_search(query: str) -> str:
    """
    Searches the web for the given query and returns a summary of top results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No web search results found."
        formatted = []
        for r in results:
            formatted.append(f"{r.get('title', '')}: {r.get('body', '')} (source: {r.get('href', '')})")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {str(e)}"
