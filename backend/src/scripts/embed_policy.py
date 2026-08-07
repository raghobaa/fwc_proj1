import asyncio
import re
from datetime import datetime, timezone
from src.config.database import get_db
from src.config.llm import get_embeddings

async def embed_policy():
    try:
        db = await get_db()
        collection = db.get_collection("policy_chunks")
        
        with open("src/data/trendly_policy.md", "r", encoding="utf-8") as f:
            policy_text = f.read()
            
        print("Policy loaded.")
        
        # Split by double newline
        raw_chunks = re.split(r'\r?\n\r?\n', policy_text)
        
        chunks = []
        for c in raw_chunks:
            c = c.strip()
            if len(c) > 20 and not re.match(r'^[-#\s]+$', c):
                chunks.append(c)
                
        print(f"Found {len(chunks)} valid chunks.")
        
        await collection.delete_many({})
        print("Old policy deleted.")
        
        embeddings = get_embeddings()
        
        for i, chunk in enumerate(chunks):
            print(f"Embedding chunk {i + 1}/{len(chunks)}")
            
            query_embedding = await embeddings.aembed_query(chunk)
            
            await collection.insert_one({
                "chunkId": i,
                "text": chunk,
                "embedding": query_embedding,
                "source": "trendly_policy.md",
                "createdAt": datetime.now(timezone.utc)
            })
            
        print(f"Successfully embedded {len(chunks)} policy chunks.")
    except Exception as e:
        print(f"Failed to embed policy: {e}")

if __name__ == "__main__":
    asyncio.run(embed_policy())
