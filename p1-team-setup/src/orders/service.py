from orders.models import Order, Priority

_PRIORITY_RANK: dict[Priority, int] = {
    Priority.HIGH: 0,
    Priority.NORMAL: 1,
    Priority.LOW: 2,
}


class OrderService:
    """In-memory order store."""

    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def create_order(
        self,
        customer: str,
        item: str,
        quantity: int,
        priority: Priority = Priority.NORMAL,
    ) -> Order:
        """Create and store a new order."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        order = Order(
            self._next_id, customer, item, quantity, priority=Priority(priority)
        )
        self._orders[order.order_id] = order
        self._next_id += 1
        return order

    def cancel_order(self, order_id: int) -> Order:
        """Cancel an existing order."""
        order = self._orders.get(order_id)
        if order is None:
            raise KeyError(f"order {order_id} not found")
        if order.status == "cancelled":
            raise ValueError("Order already cancelled")
        order.status = "cancelled"
        return order

    def list_orders(self) -> list[Order]:
        """Return all orders, highest priority first, oldest first within a priority."""
        return sorted(
            self._orders.values(),
            key=lambda o: (_PRIORITY_RANK[o.priority], o.order_id),
        )
