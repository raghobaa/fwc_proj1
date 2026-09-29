import os
import re
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Initialize MongoDB connection at module level
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client["trendly"]
orders_collection = db["orders"]
customers_collection = db["customers"]

def get_order(order_id: str, customer_id: str) -> dict:
    """Retrieve an order belonging to the authenticated customer."""
    order = orders_collection.find_one({"order_id": {"$regex": f"^{order_id}$", "$options": "i"}})

    if not order:
        return {
            "found": False,
            "message": "Order not found."
        }
    
    if order.get("customer_id") != customer_id:
        return {
            "found": False,
            "message": "This order does not belong to the authenticated customer."
        }

    # Convert MongoDB ObjectId to string if present
    if "_id" in order:
        order["_id"] = str(order["_id"])

    return_info = None
    if order.get("delivered_at"):
        # We need a timezone-aware current time to compare with parsed dates if they have TZ info
        today = datetime.now(timezone.utc)
        
        # Parse delivered_at (e.g. 2026-07-14T09:20:00Z)
        delivered_date_str = order["delivered_at"]
        if delivered_date_str.endswith('Z'):
            delivered_date_str = delivered_date_str[:-1] + '+00:00'
        
        delivered_date = datetime.fromisoformat(delivered_date_str)
        return_deadline = delivered_date + timedelta(days=30)
        
        eligible = today <= return_deadline
        
        days_remaining = (return_deadline - today).days
        
        return_info = {
            "eligible": eligible,
            "deliveredDate": delivered_date.strftime("%Y-%m-%d"),
            "deadline": return_deadline.strftime("%Y-%m-%d"),
            "daysRemaining": max(days_remaining, 0)
        }

    return {
        "found": True,
        "order": order,
        "returnInfo": return_info
    }

def customer_exists(customer_id: str) -> bool:
    """Check if a customer exists."""
    return customers_collection.count_documents({"customer_id": customer_id}) > 0

def get_customer_id_by_email(email: str):
    """Resolve a customer ID from the authenticated email, or None if unknown."""
    if not email:
        return None
    customer = customers_collection.find_one({"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}})
    return customer.get("customer_id") if customer else None
