import asyncio
import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

REFUND_APPROVAL_THRESHOLD = int(os.getenv("REFUND_APPROVAL_THRESHOLD", "20000"))
MAX_ORDER_LOOKUP_ATTEMPTS = 3
ORDER_LOOKUP_TIMEOUT_SECONDS = 5

NON_RETURNABLE_CATEGORIES = {
    "innerwear",
    "socks",
    "jewellery",
    "beauty",
    "fragrance",
    "face_masks",
    "gift_cards",
}

RETURNS_FILE = Path(__file__).resolve().parents[1] / "data" / "returns.json"

# Planner: the ordered steps used to process every return request.
PLANNER_STEPS = [
    "find_order",
    "check_return_policy",
    "verify_eligibility",
    "compute_refund",
    "create_return",
]

# ── Order lookup (with retry) ───────────────────────────────────────────────

async def lookup_order_with_retry(order_id: str, customer_id: str) -> dict:
    """Look up an order, retrying up to MAX_ORDER_LOOKUP_ATTEMPTS on timeout."""
    from src.tools.order_tool import get_order

    last_error = None
    for attempt in range(1, MAX_ORDER_LOOKUP_ATTEMPTS + 1):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(get_order, order_id, customer_id),
                timeout=ORDER_LOOKUP_TIMEOUT_SECONDS,
            )
            result["attempts"] = attempt
            return result
        except asyncio.TimeoutError as e:
            last_error = e
        except Exception as e:
            result = {
                "found": False,
                "attempts": attempt,
                "message": f"Order lookup failed: {e}",
            }
            return result

    return {
        "found": False,
        "attempts": MAX_ORDER_LOOKUP_ATTEMPTS,
        "message": f"Order lookup timed out after {MAX_ORDER_LOOKUP_ATTEMPTS} attempts. Please try again later.",
    }

# ── Policy check ────────────────────────────────────────────────────────────

async def check_return_policy() -> dict:
    """Retrieve the official return/refund policy context to ground the response."""
    from src.tools.policy_tool import search_policy

    return await search_policy(
        "return eligibility window non-returnable categories final sale items refund approval"
    )

# ── Eligibility ─────────────────────────────────────────────────────────────

def evaluate_eligibility(order: dict, return_info: dict | None) -> dict:
    """Deterministically check return eligibility against the official policy."""
    issues = []

    status = (order.get("status") or "").lower()
    if status == "cancelled":
        return {
            "eligible": False,
            "issues": ["This order was cancelled; a return cannot be raised against a cancelled order."],
            "refundableTotal": 0,
            "exchangeOnlyItems": [],
            "hasFinalSaleItems": False,
        }
    if status == "lost_in_transit":
        return {
            "eligible": False,
            "issues": ["This parcel is marked lost. This is a lost-parcel claim, not a return, and must be handled by a human support agent."],
            "refundableTotal": 0,
            "exchangeOnlyItems": [],
            "hasFinalSaleItems": False,
        }

    # Window check (30 calendar days from delivery)
    window_ok = True
    if order.get("delivered_at"):
        window_ok = bool(return_info and return_info.get("eligible"))
        if not window_ok:
            issues.append(
                f"The 30-day return window expired on {return_info['deadline']}."
            )

    items = order.get("items", [])
    refundable_total = 0
    exchange_only = []
    excluded = []

    for item in items:
        category = (item.get("category") or "").lower().replace(" ", "_")
        if category in NON_RETURNABLE_CATEGORIES:
            excluded.append(f"{item.get('name')} (non-returnable category: {item.get('category')})")
            continue
        if item.get("final_sale"):
            exchange_only.append(item.get("name"))
            continue
        if window_ok:
            refundable_total += item.get("price", 0) * item.get("qty", 1)

    if excluded:
        issues.append("Non-returnable item(s) excluded from the refund: " + ", ".join(excluded))

    eligible = window_ok and refundable_total > 0

    return {
        "eligible": eligible,
        "issues": issues,
        "refundableTotal": refundable_total,
        "exchangeOnlyItems": exchange_only,
        "hasFinalSaleItems": len(exchange_only) > 0,
        "exchangeOnly": window_ok and refundable_total == 0 and len(exchange_only) > 0,
    }

# ── Reflection ──────────────────────────────────────────────────────────────

def reflect(order_result: dict, eligibility: dict, policy_result: dict) -> list:
    """Reflection pass: sanity-check the whole decision before proceeding."""
    notes = []

    if not order_result.get("found"):
        notes.append("Order not found or does not belong to the customer.")
    if not policy_result.get("found"):
        notes.append("No official policy context was retrieved; proceeding with policy knowledge only.")
    if order_result.get("found") and order_result.get("order", {}).get("order_id"):
        notes.append(f"Order ID verified: {order_result['order']['order_id']}.")
    for issue in eligibility.get("issues", []):
        notes.append(issue)

    return notes

# ── Refund + human approval gate ────────────────────────────────────────────

def compute_refund(eligibility: dict) -> dict:
    """Compute the refund and decide whether human approval is required."""
    amount = eligibility.get("refundableTotal") or 0
    requires_approval = amount > REFUND_APPROVAL_THRESHOLD
    return {
        "refundAmount": amount,
        "requiresApproval": requires_approval,
        "approvalReason": (
            f"Refund amount Rs. {amount:,} exceeds the Rs. {REFUND_APPROVAL_THRESHOLD:,} "
            "threshold and requires human approval."
            if requires_approval
            else None
        ),
    }

# ── Create return record ────────────────────────────────────────────────────

def _read_returns() -> list:
    if not RETURNS_FILE.exists():
        return []
    try:
        with open(RETURNS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def _write_returns(records: list):
    RETURNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RETURNS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def create_return_record(order_id: str, customer_id: str, reason: str, refund: dict) -> dict:
    records = _read_returns()
    return_id = f"RET-{random.randint(10000, 99999)}"
    record = {
        "returnId": return_id,
        "orderId": order_id,
        "customerId": customer_id,
        "reason": reason,
        "refundAmount": refund["refundAmount"],
        "requiresApproval": refund["requiresApproval"],
        "status": "PENDING_APPROVAL" if refund["requiresApproval"] else "RAISED",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    records.append(record)
    _write_returns(records)

    # Persist to MongoDB returns collection if connected
    try:
        from pymongo import MongoClient
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        m_client = MongoClient(uri, serverSelectionTimeoutMS=1000)
        m_client["trendly"]["returns"].insert_one(dict(record))
    except Exception:
        pass

    return record


# ── Orchestrator ────────────────────────────────────────────────────────────

async def process_return_request(order_id: str, customer_id: str, reason: str) -> dict:
    """Run the full return pipeline: plan, lookup (retry), policy, eligibility, reflection, refund, create."""
    plan = PLANNER_STEPS

    order_result = await lookup_order_with_retry(order_id, customer_id)
    if not order_result.get("found"):
        return {
            "success": False,
            "plan": plan,
            "message": order_result.get("message", "Order could not be found."),
            "orderId": order_id,
            "reflection": [order_result.get("message", "Order not found.")],
        }

    order = order_result["order"]
    return_info = order_result.get("returnInfo")

    policy_result = await check_return_policy()
    eligibility = evaluate_eligibility(order, return_info)
    reflection = reflect(order_result, eligibility, policy_result)

    if not eligibility["eligible"] and eligibility.get("exchangeOnly"):
        return {
            "success": False,
            "plan": plan,
            "orderId": order_id,
            "reflection": reflection,
            "exchangeOnlyItems": eligibility["exchangeOnlyItems"],
            "message": "This order contains final sale item(s), which are eligible for size exchange only, not refunds.",
        }

    if not eligibility["eligible"]:
        return {
            "success": False,
            "plan": plan,
            "orderId": order_id,
            "reflection": reflection,
            "issues": eligibility["issues"],
            "message": "Return is not eligible under the official Trendly policy.",
        }

    refund = compute_refund(eligibility)
    record = create_return_record(order_id, customer_id, reason, refund)

    return {
        "success": True,
        "plan": plan,
        "orderId": order_id,
        "returnId": record["returnId"],
        "refundAmount": refund["refundAmount"],
        "requiresApproval": refund["requiresApproval"],
        "approvalReason": refund["approvalReason"],
        "status": record["status"],
        "reflection": reflection,
        "message": (
            "Return created. Refund will be processed after the item is received and "
            "passes inspection." if not refund["requiresApproval"] else
            "Return submitted. The refund exceeds the approval threshold, so a human "
            "agent will review and approve it before processing."
        ),
    }
