# Summary format agreed with support team, 24 Oct
from orders.models import Order, Priority

_KNOWN_STATUSES = {"created", "cancelled"}


def format_order_summary(order: Order) -> str:
    """Return a one-line text summary of an order for a customer email."""
    if order.status not in _KNOWN_STATUSES:
        raise ValueError(f"unknown order status: {order.status!r}")
    noun = "item" if order.quantity == 1 else "items"
    parts = [f"Order {order.order_id}", f"{order.quantity} {noun}"]
    if order.priority != Priority.NORMAL:
        parts.append(f"{order.priority} priority")
    parts.append(order.status)
    return " · ".join(parts)
