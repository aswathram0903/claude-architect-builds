import pytest

from orders.models import Priority
from orders.service import OrderService


@pytest.fixture
def mixed_priority_service() -> OrderService:
    """Build a service holding low, high, normal, high orders (ids 1-4)."""
    service = OrderService()
    service.create_order("ann", "pen", 1, Priority.LOW)
    service.create_order("bob", "ink", 1, Priority.HIGH)
    service.create_order("cat", "cap", 1, Priority.NORMAL)
    service.create_order("dan", "bag", 1, Priority.HIGH)
    return service


def test_create_order_assigns_incrementing_ids():
    service = OrderService()
    assert service.create_order("ann", "pen", 1).order_id == 1
    assert service.create_order("bob", "ink", 2).order_id == 2


def test_create_order_rejects_non_positive_quantity():
    with pytest.raises(ValueError):
        OrderService().create_order("ann", "pen", 0)


def test_cancel_order_sets_status_cancelled():
    service = OrderService()
    order = service.create_order("ann", "pen", 1)
    assert service.cancel_order(order.order_id).status == "cancelled"


def test_cancel_order_unknown_id_raises_key_error():
    with pytest.raises(KeyError):
        OrderService().cancel_order(99)


def test_list_orders_returns_all_orders():
    service = OrderService()
    service.create_order("ann", "pen", 1)
    service.create_order("bob", "ink", 2)
    assert len(service.list_orders()) == 2


def test_cancel_order_already_cancelled_raises_value_error():
    service = OrderService()
    order = service.create_order("ann", "pen", 1)
    service.cancel_order(order.order_id)
    with pytest.raises(ValueError, match="Order already cancelled"):
        service.cancel_order(order.order_id)


def test_create_order_defaults_priority_to_normal():
    assert OrderService().create_order("ann", "pen", 1).priority == Priority.NORMAL


def test_create_order_invalid_priority_raises_value_error():
    with pytest.raises(ValueError):
        OrderService().create_order("ann", "pen", 1, "urgent")


def test_list_orders_sorts_by_priority_then_age(mixed_priority_service):
    ids = [o.order_id for o in mixed_priority_service.list_orders()]
    assert ids == [2, 4, 3, 1]
