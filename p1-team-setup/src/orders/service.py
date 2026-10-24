from orders.models import Order


class OrderService:
    """In-memory order store."""

    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def create_order(self, customer: str, item: str, quantity: int) -> Order:
        """Create and store a new order."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        order = Order(self._next_id, customer, item, quantity)
        self._orders[order.order_id] = order
        self._next_id += 1
        return order

    def cancel_order(self, order_id: int) -> Order:
        """Cancel an existing order."""
        order = self._orders.get(order_id)
        if order is None:
            raise KeyError(f"order {order_id} not found")
        order.status = "cancelled"
        return order

    def list_orders(self) -> list[Order]:
        """Return all orders in creation order."""
        return list(self._orders.values())
