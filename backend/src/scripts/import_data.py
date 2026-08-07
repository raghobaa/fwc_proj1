import json
import asyncio
from src.config.database import get_db

async def import_data():
    try:
        db = await get_db()
        customers_collection = db.get_collection("customers")
        orders_collection = db.get_collection("orders")
        
        with open("src/data/orders.json", "r") as f:
            data = json.load(f)
            
        print("JSON data loaded.")
        
        await customers_collection.delete_many({})
        await orders_collection.delete_many({})
        print("Cleared old customer and order records.")
        
        if data.get("customers"):
            await customers_collection.insert_many(data["customers"])
            print(f"Successfully imported {len(data['customers'])} customers.")
            
        if data.get("orders"):
            await orders_collection.insert_many(data["orders"])
            print(f"Successfully imported {len(data['orders'])} orders.")
            
    except Exception as e:
        print(f"Failed to import JSON data: {e}")

if __name__ == "__main__":
    asyncio.run(import_data())
