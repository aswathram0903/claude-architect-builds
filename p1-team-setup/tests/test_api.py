import pytest

from orders import api
from orders.service import OrderService


@pytest.fixture(autouse=True)
def fresh_service(monkeypatch):
    monkeypatch.setattr(api, "_service", OrderService())


def test_create_order_returns_created_order():
    order = api.create_order("ann", "pen", 3)
    assert (order.customer, order.status) == ("ann", "created")


def test_cancel_order_marks_order_cancelled():
    order = api.create_order("ann", "pen", 3)
    assert api.cancel_order(order.order_id).status == "cancelled"


def test_list_orders_reflects_created_orders():
    api.create_order("ann", "pen", 1)
    assert len(api.list_orders()) == 1
