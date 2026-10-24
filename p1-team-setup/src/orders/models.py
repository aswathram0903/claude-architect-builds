from dataclasses import dataclass
from enum import StrEnum


class Priority(StrEnum):
    """Urgency level of an order."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class Order:
    """A customer order and its current status."""

    order_id: int
    customer: str
    item: str
    quantity: int
    status: str = "created"
    priority: Priority = Priority.NORMAL
