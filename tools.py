import json
from datetime import datetime

# Load orders.json once
with open("orders.json", "r", encoding="utf-8") as f:
    ORDER_DATA = json.load(f)

ORDERS = ORDER_DATA["orders"]


def lookup_order(order_id):
    """Find an order by Order ID."""
    order_id = order_id.strip().upper()

    for order in ORDERS:
        if order["order_id"].upper() == order_id:
            return order

    return None


def check_return_eligibility(order_id):
    """
    Checks whether an order is eligible for return or exchange.
    Returns a dictionary with eligibility and message.
    """

    order = lookup_order(order_id)

    if not order:
        return {
            "eligible": False,
            "message": "Order not found."
        }

    status = order["status"]

    # 1. Already cancelled
    if status == "cancelled":
        return {
            "eligible": False,
            "message": "This order was already cancelled and refunded, so a return cannot be created."
        }

    # 2. Lost parcel
    if status == "lost_in_transit":
        return {
            "eligible": False,
            "message": "This shipment appears to be lost in transit. I'll escalate this to a human support specialist."
        }

    # 3. Must be delivered first
    if status != "delivered":
        return {
            "eligible": False,
            "message": f"This order is currently '{status.replace('_', ' ')}'. Returns are available only after delivery."
        }

    # Delivery date
    delivered_date = datetime.strptime(
        order["delivered_at"][:10],
        "%Y-%m-%d"
    )

    # Fixed evaluation date for Yellow.ai assignment
    today = datetime.strptime("2026-08-18", "%Y-%m-%d")
    days_since_delivery = (today - delivered_date).days

    item = order["items"][0]

    # 4. Jewellery restriction (checked BEFORE date)
    if item["category"] == "jewellery":
        return {
            "eligible": False,
            "message": "Jewellery items are non-returnable for hygiene reasons."
        }

    # 5. Final Sale restriction (checked BEFORE date)
    if item.get("final_sale"):
        return {
            "eligible": "exchange_only",
            "message": "This item was purchased as FINAL SALE and is eligible for exchange only, not a refund."
        }

    # 6. Outside return window
    if days_since_delivery > 30:
        return {
            "eligible": False,
            "message": f"This order was delivered {days_since_delivery} days ago, which is outside Trendly's 30-day return window."
        }

    # 7. Happy path
    return {
        "eligible": True,
        "message": f"{item['name']} is eligible for return. Your return request has been initiated.",
        "item": item["name"],
        "order_id": order["order_id"]
    }

def escalate_to_human(order_id, customer_issue):
    """
    Creates a human-readable escalation summary.
    """

    order = lookup_order(order_id)

    if not order:
        return "Unable to escalate because the order was not found."

    summary = f"""
🚨 HUMAN ESCALATION REQUIRED

Order ID: {order["order_id"]}

Customer Issue:
{customer_issue}

Order Status:
{order["status"].replace("_"," ").title()}

Item:
{order["items"][0]["name"]}

Carrier:
{order["carrier"]}

Shipping City:
{order["shipping_city"]}

Recommended Action:
A human support specialist should review this shipment and contact the customer.
"""

    return summary
