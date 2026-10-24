from orders.models import Order
from orders.service import OrderService

_service = OrderService()


def create_order(customer: str, item: str, quantity: int) -> Order:
    """Create an order via the shared service."""
    return _service.create_order(customer, item, quantity)


def cancel_order(order_id: int) -> Order:
    """Cancel an order via the shared service."""
    return _service.cancel_order(order_id)


def list_orders() -> list[Order]:
    """List all orders from the shared service."""
    return _service.list_orders()
