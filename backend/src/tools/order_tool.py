import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

ORDERS_FILE = Path(__file__).resolve().parents[1] / "data" / "orders.json"

# Initialize MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    db = client["trendly"]
    orders_collection = db["orders"]
    customers_collection = db["customers"]
except Exception:
    client = None
    db = None
    orders_collection = None
    customers_collection = None

def _get_local_data():
    if not ORDERS_FILE.exists():
        return {"customers": [], "orders": []}
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"customers": [], "orders": []}

def get_order(order_id: str, customer_id: str = None) -> dict:
    """Retrieve an order belonging to the authenticated customer, or any order if customer_id is None/ADMIN."""
    order = None
    if orders_collection is not None:
        try:
            order = orders_collection.find_one({"order_id": {"$regex": f"^{order_id}$", "$options": "i"}})
        except Exception as e:
            print(f"[Order Tool] Mongo lookup failed ({e}), using local orders.json")
            order = None

    if order is None:
        local_data = _get_local_data()
        order_id_clean = order_id.strip().lower()
        for o in local_data.get("orders", []):
            if o.get("order_id", "").strip().lower() == order_id_clean:
                order = dict(o)
                break

    if not order:
        return {
            "found": False,
            "message": "Order not found."
        }
    
    if customer_id and customer_id != "ADMIN" and order.get("customer_id") != customer_id:
        return {
            "found": False,
            "message": "This order does not belong to the authenticated customer."
        }


    # Convert MongoDB ObjectId to string if present
    if "_id" in order:
        order["_id"] = str(order["_id"])

    return_info = None
    if order.get("delivered_at"):
        today = datetime.now(timezone.utc)
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
    if customers_collection is not None:
        try:
            return customers_collection.count_documents({"customer_id": customer_id}) > 0
        except Exception:
            pass
    local_data = _get_local_data()
    return any(c.get("customer_id") == customer_id for c in local_data.get("customers", []))

def get_customer_id_by_email(email: str):
    """Resolve a customer ID from the authenticated email, or None if unknown."""
    if not email:
        return None
    if customers_collection is not None:
        try:
            customer = customers_collection.find_one({"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}})
            if customer:
                return customer.get("customer_id")
        except Exception:
            pass
    local_data = _get_local_data()
    email_clean = email.strip().lower()
    for c in local_data.get("customers", []):
        if c.get("email", "").strip().lower() == email_clean:
            return c.get("customer_id")
    return None

