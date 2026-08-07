from src.config.gemini import get_embeddings
from src.config.database import get_db

async def search_policy(query: str) -> dict:
    from src.rag.retriever import retrieve_policy_context
    results = await retrieve_policy_context(query)
    
    return {
        "found": len(results) > 0,
        "context": results,
        "message": "Relevant policy found." if len(results) > 0 else "No relevant policy found in the official Trendly policy."
    }
