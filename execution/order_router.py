class OrderRouter:
    """Stub router that prints orders for execution."""

    def route_order(self, order: dict) -> str:
        print(f"Routing order: {order}")
        return "routed"
