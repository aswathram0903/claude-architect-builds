from dataclasses import dataclass


@dataclass
class Order:
    """A customer order and its current status."""

    order_id: int
    customer: str
    item: str
    quantity: int
    status: str = "created"
