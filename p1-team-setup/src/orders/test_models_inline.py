from orders.models import Order


def test_order_defaults_status_to_created() -> None:
    """Verify a new order starts with the created status."""
    assert Order(1, "ann", "pen", 1).status == "created"
