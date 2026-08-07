from src.config.llm import get_embeddings
from src.config.database import get_db

async def retrieve_policy_context(query: str) -> list:
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
    
    return results
