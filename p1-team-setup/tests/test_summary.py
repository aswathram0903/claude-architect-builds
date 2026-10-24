import pytest

from orders.models import Order, Priority
from orders.summary import format_order_summary


@pytest.fixture
def high_priority_order() -> Order:
    """Build a created, high-priority order for 3 items."""
    return Order("A-17", "ann", "pen", 3, "created", Priority.HIGH)


@pytest.fixture
def cancelled_order() -> Order:
    """Build a cancelled, normal-priority order for 1 item."""
    return Order("B-2", "bob", "ink", 1, "cancelled", Priority.NORMAL)


def test_format_order_summary_high_priority_shows_priority_and_plural_items(
    high_priority_order,
):
    assert format_order_summary(high_priority_order) == (
        "Order A-17 · 3 items · high priority · created"
    )


def test_format_order_summary_normal_priority_cancelled_hides_priority_and_singular_item(
    cancelled_order,
):
    assert format_order_summary(cancelled_order) == "Order B-2 · 1 item · cancelled"


def test_format_order_summary_unknown_status_raises_value_error(cancelled_order):
    cancelled_order.status = "shipped"
    with pytest.raises(ValueError, match="unknown order status"):
        format_order_summary(cancelled_order)
