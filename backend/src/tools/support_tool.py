import random

async def create_support_ticket(reason: str, customer_id: str) -> dict:
    ticket_id = f"SUP-{random.randint(1000, 9999)}"
    
    return {
        "success": True,
        "ticketId": ticket_id,
        "customerId": customer_id,
        "reason": reason,
        "status": "OPEN",
        "assignedTo": "Human Support Team",
        "message": "A support ticket has been created successfully. Our support team will contact you shortly.",
    }
