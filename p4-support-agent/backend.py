"""Fake support backend for P4. All data is invented."""

CUSTOMERS = {
    "anna@example.com": {"customer_id": "C-100", "name": "Anna Berg", "tier": "standard"},
    "omar@example.com": {"customer_id": "C-200", "name": "Omar Ali", "tier": "gold"},
}

ORDERS = {
    "A-5001": {"customer_id": "C-100", "item": "Desk lamp", "amount": 49.0, "status": "delivered", "damage_photo": True},
    "A-5002": {"customer_id": "C-100", "item": "Office chair", "amount": 640.0, "status": "delivered", "damage_photo": False},
    "A-7001": {"customer_id": "C-200", "item": "Monitor", "amount": 310.0, "status": "in transit", "damage_photo": False},
}

_flaky = {"A-7001": 1}  # the first lookup of this order fails with a temporary error


def error(category: str, message: str, retryable: bool) -> dict:
    """A structured error: what kind of failure, whether a retry can help, and a message for people."""
    return {"isError": True, "errorCategory": category, "isRetryable": retryable, "message": message}


def get_customer(email: str) -> dict:
    customer = CUSTOMERS.get(email.strip().lower())
    if not customer:
        return error("validation", f"No customer with email {email}.", False)
    return dict(customer)


def lookup_order(order_id: str, customer_id: str) -> dict:
    if _flaky.get(order_id, 0) > 0:
        _flaky[order_id] -= 1
        return error("transient", "The order service timed out. Trying again may work.", True)
    order = ORDERS.get(order_id)
    if not order:
        return error("validation", f"No order {order_id}.", False)
    if order["customer_id"] != customer_id:
        return error("permission", "This order belongs to a different customer.", False)
    return {"order_id": order_id, **order}


def process_refund(order_id: str, amount: float) -> dict:
    order = ORDERS[order_id]
    if order["status"] != "delivered":
        return error("business", "Refunds are only possible after delivery.", False)
    if amount > order["amount"]:
        return error("validation", f"Refund {amount} is more than the order amount {order['amount']}.", False)
    return {"refund_id": f"R-{order_id}", "amount": amount, "status": "issued"}


def escalate_to_human(summary: str, reason: str) -> dict:
    return {"ticket_id": "H-001", "status": "queued for a human agent", "reason": reason}
