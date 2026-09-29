import os
import json
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

RETURNS_FILE = Path(__file__).resolve().parents[1] / "data" / "returns.json"
ORDERS_FILE = Path(__file__).resolve().parents[1] / "data" / "orders.json"

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    db = client["trendly"]
    returns_collection = db["returns"]
    orders_collection = db["orders"]
except Exception:
    client = None
    db = None
    returns_collection = None
    orders_collection = None

def _read_local_returns() -> list:
    if not RETURNS_FILE.exists():
        return []
    try:
        with open(RETURNS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _write_local_returns(data: list):
    RETURNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RETURNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_pending_returns(filter_high_value: bool = False) -> dict:
    """List all returns currently pending approval."""
    records = []
    if returns_collection is not None:
        try:
            records = list(returns_collection.find({"status": "PENDING_APPROVAL"}))
            for r in records:
                if "_id" in r:
                    r["_id"] = str(r["_id"])
        except Exception:
            records = []
            
    if not records:
        all_local = _read_local_returns()
        records = [r for r in all_local if r.get("status") == "PENDING_APPROVAL"]
        
    if filter_high_value:
        records = [r for r in records if r.get("refundAmount", 0) > 20000]

    return {
        "success": True,
        "count": len(records),
        "pendingReturns": records,
        "message": f"Found {len(records)} returns pending approval." if records else "No returns currently pending approval."
    }

def get_all_returns(status: str = None) -> dict:
    """List all returns, optionally filtered by status."""
    records = []
    if returns_collection is not None:
        try:
            query = {"status": status} if status else {}
            records = list(returns_collection.find(query))
            for r in records:
                if "_id" in r:
                    r["_id"] = str(r["_id"])
        except Exception:
            records = []

    if not records:
        all_local = _read_local_returns()
        if status:
            records = [r for r in all_local if r.get("status", "").upper() == status.upper()]
        else:
            records = all_local

    return {
        "success": True,
        "count": len(records),
        "returns": records
    }

def approve_return_by_id(return_id: str, admin_email: str = "admin@trendly.com", note: str = None) -> dict:
    """Approve a pending return and authorize refund."""
    return_id_clean = return_id.strip().upper()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Update Mongo if available
    updated = False
    if returns_collection is not None:
        try:
            res = returns_collection.update_one(
                {"returnId": {"$regex": f"^{return_id_clean}$", "$options": "i"}},
                {"$set": {
                    "status": "APPROVED",
                    "approvedBy": admin_email,
                    "approvedAt": now_iso,
                    "approvalNote": note or "Approved by Admin"
                }}
            )
            if res.modified_count > 0:
                updated = True
        except Exception:
            pass

    # 2. Update local JSON file
    local_returns = _read_local_returns()
    found_record = None
    for r in local_returns:
        if r.get("returnId", "").strip().upper() == return_id_clean:
            r["status"] = "APPROVED"
            r["approvedBy"] = admin_email
            r["approvedAt"] = now_iso
            r["approvalNote"] = note or "Approved by Admin"
            found_record = r
            updated = True
            break
            
    if updated:
        _write_local_returns(local_returns)
        return {
            "success": True,
            "returnId": return_id_clean,
            "status": "APPROVED",
            "approvedBy": admin_email,
            "refundAmount": found_record.get("refundAmount") if found_record else None,
            "orderId": found_record.get("orderId") if found_record else None,
            "message": f"Return {return_id_clean} has been successfully APPROVED. Refund authorization processed."
        }
    else:
        return {
            "success": False,
            "message": f"Return ID {return_id} not found."
        }

def reject_return_by_id(return_id: str, admin_email: str = "admin@trendly.com", reason: str = "Rejected by Admin") -> dict:
    """Reject a pending return."""
    return_id_clean = return_id.strip().upper()
    now_iso = datetime.now(timezone.utc).isoformat()

    updated = False
    if returns_collection is not None:
        try:
            res = returns_collection.update_one(
                {"returnId": {"$regex": f"^{return_id_clean}$", "$options": "i"}},
                {"$set": {
                    "status": "REJECTED",
                    "rejectedBy": admin_email,
                    "rejectedAt": now_iso,
                    "rejectionReason": reason
                }}
            )
            if res.modified_count > 0:
                updated = True
        except Exception:
            pass

    local_returns = _read_local_returns()
    found_record = None
    for r in local_returns:
        if r.get("returnId", "").strip().upper() == return_id_clean:
            r["status"] = "REJECTED"
            r["rejectedBy"] = admin_email
            r["rejectedAt"] = now_iso
            r["rejectionReason"] = reason
            found_record = r
            updated = True
            break

    if updated:
        _write_local_returns(local_returns)
        return {
            "success": True,
            "returnId": return_id_clean,
            "status": "REJECTED",
            "rejectedBy": admin_email,
            "reason": reason,
            "message": f"Return {return_id_clean} has been REJECTED. Reason: {reason}."
        }
    else:
        return {
            "success": False,
            "message": f"Return ID {return_id} not found."
        }
