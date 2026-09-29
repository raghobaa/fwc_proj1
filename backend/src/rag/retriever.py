import os
import re
from pathlib import Path
from src.config.llm import get_embeddings
from src.config.database import get_db

POLICY_FILE_PATH = Path(__file__).resolve().parents[1] / "data" / "trendly_policy.md"

def _get_local_policy_chunks() -> list[str]:
    """Read local trendly_policy.md and chunk by numbered subsections / major headings."""
    if not POLICY_FILE_PATH.exists():
        return []
    with open(POLICY_FILE_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Split by subsection headers like **1.1 ..., **2.3 ..., ## 1. ..., etc.
    sections = re.split(r'(?=\n(?:\*\*|\#\#\s*)\d+(?:\.\d+)?)', text)
    chunks = []
    for s in sections:
        s = s.strip()
        if len(s) > 20 and not s.startswith("# Trendly") and not s.startswith("*Effective 1 January"):
            chunks.append(s)
    return chunks


def _search_local_policy(query: str, limit: int = 5) -> list[dict]:
    """Fallback keyword / relevance search over local policy chunks."""
    chunks = _get_local_policy_chunks()
    if not chunks:
        return []

    tokens = [t.lower() for t in re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', query)]
    if not tokens:
        tokens = query.lower().split()

    # Filter generic stop words for higher precision
    stop_words = {"what", "tell", "about", "your", "the", "and", "our", "company", "info", "information", "like", "know"}
    substantive_tokens = [t for t in tokens if t not in stop_words]
    if not substantive_tokens:
        substantive_tokens = tokens

    scored_chunks = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = 0
        for token in substantive_tokens:
            # Count exact word or substring occurrences
            count = chunk_lower.count(token)
            if count > 0:
                # Weight specific high-value terms more than generic word 'policy'
                weight = 1 if token == "policy" else 3
                score += count * weight
                if f"**" in chunk_lower and token in chunk_lower:
                    score += 2
                if f"##" in chunk_lower and token in chunk_lower:
                    score += 2
        if score > 0:
            scored_chunks.append({"text": chunk, "score": score})

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    if not scored_chunks:
        return [{"text": c, "score": 1.0} for c in chunks[:limit]]
    return scored_chunks[:limit]


async def retrieve_policy_context(query: str) -> list:
    """Retrieve policy context using MongoDB Atlas vector search with local fallback."""
    try:
        db = await get_db()
        collection = db.get_collection("policy_chunks")
        
        embeddings = get_embeddings()
        query_embedding = await embeddings.aembed_query(query)
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "embedding",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 20,
                    "limit": 3
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=3)
        if results:
            return results
    except Exception as e:
        print(f"[RAG Retriever] Atlas vector search failed ({e}), using local policy fallback.")
    
    # Fallback to local policy file search
    return _search_local_policy(query, limit=3)

