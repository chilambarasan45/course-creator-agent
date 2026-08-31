from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Semantic chunker - groups sentences by topic similarity
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
semantic_splitter = SemanticChunker(embeddings_model)

# Fallback splitter - used only if a semantic chunk is too large
fallback_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)


def chunk_text(text: str, max_chunk_size: int = 800) -> list[str]:
    """
    Splits text semantically (by topic), then further splits any
    chunk that's too large using recursive character splitting.
    """
    semantic_chunks = semantic_splitter.split_text(text)

    final_chunks = []
    for chunk in semantic_chunks:
        if len(chunk) > max_chunk_size:
            # too big — split further
            sub_chunks = fallback_splitter.split_text(chunk)
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)

    return final_chunks