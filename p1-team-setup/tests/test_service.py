import pytest

from orders.service import OrderService


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
