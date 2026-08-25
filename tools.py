import json
from datetime import datetime
import uuid

# ---------------- LOAD ORDERS ----------------
with open("orders.json", "r", encoding="utf-8") as f:
    ORDER_DATA = json.load(f)

ORDERS = ORDER_DATA["orders"]

# Fixed evaluation date for assignment
TODAY = datetime.strptime("2026-08-18", "%Y-%m-%d")
RETURN_WINDOW = 30


# ---------------- ORDER LOOKUP ----------------
def lookup_order(order_id):
    order_id = order_id.strip().upper()

    for order in ORDERS:
        if order["order_id"].upper() == order_id:
            return order

    return None


# ---------------- RETURN / EXCHANGE ELIGIBILITY ----------------
def check_return_eligibility(order_id):

    order = lookup_order(order_id)

    if not order:
        return {
            "eligible": False,
            "message": "Order not found.",
            "item": None,
            "order_id": order_id,
            "days_since_delivery": None,
            "days_remaining": None
        }

    status = order["status"]
    item = order["items"][0]

    # Cancelled orders
    if status == "cancelled":
        return {
            "eligible": False,
            "message": "This order has already been cancelled and refunded.",
            "item": item["name"],
            "order_id": order_id,
            "days_since_delivery": None,
            "days_remaining": None
        }

    # Lost shipment
    if status == "lost_in_transit":
        return {
            "eligible": False,
            "message": "This shipment is marked as lost in transit and requires human support.",
            "item": item["name"],
            "order_id": order_id,
            "days_since_delivery": None,
            "days_remaining": None
        }

    # Not delivered yet
    if status != "delivered":
        return {
            "eligible": False,
            "message": f"This order is currently '{status.replace('_',' ')}'. Returns are only available after delivery.",
            "item": item["name"],
            "order_id": order_id,
            "days_since_delivery": None,
            "days_remaining": None
        }

    # Delivery date calculation
    delivered_date = datetime.strptime(
        order["delivered_at"][:10],
        "%Y-%m-%d"
    )

    days_since_delivery = (TODAY - delivered_date).days
    days_remaining = max(0, RETURN_WINDOW - days_since_delivery)

    # Jewellery restriction
    if item["category"].lower() == "jewellery":
        return {
            "eligible": False,
            "message": "Jewellery items are non-returnable according to Trendly policy.",
            "item": item["name"],
            "order_id": order_id,
            "days_since_delivery": days_since_delivery,
            "days_remaining": days_remaining
        }

    # Final Sale
    if item.get("final_sale", False):
        return {
            "eligible": "exchange_only",
            "message": "This item was purchased as Final Sale and is eligible for exchange only.",
            "item": item["name"],
            "order_id": order_id,
            "days_since_delivery": days_since_delivery,
            "days_remaining": days_remaining
        }

    # Outside return window
    if days_since_delivery > RETURN_WINDOW:
        return {
            "eligible": False,
            "message": f"This order was delivered {days_since_delivery} days ago, which exceeds Trendly's 30-day return window.",
            "item": item["name"],
            "order_id": order_id,
            "days_since_delivery": days_since_delivery,
            "days_remaining": 0
        }

    # Eligible
    return {
        "eligible": True,
        "message": f"{item['name']} is eligible for return under Trendly's 30-day return policy.",
        "item": item["name"],
        "order_id": order_id,
        "days_since_delivery": days_since_delivery,
        "days_remaining": days_remaining
    }


# ---------------- HUMAN ESCALATION ----------------
def escalate_to_human(order_id, customer_issue):

    order = lookup_order(order_id)

    if not order:
        return "Unable to create escalation because the order was not found."

    ticket_id = f"ESC-{str(uuid.uuid4())[:8].upper()}"

    summary = f"""
Ticket ID: {ticket_id}

Issue Category: Customer Support Escalation

Order ID: {order["order_id"]}

Customer: {order["customer_name"]}

Issue Reported:
{customer_issue}

Order Status:
{order["status"].replace("_"," ").title()}

Item:
{order["items"][0]["name"]}

Carrier:
{order.get("carrier","N/A")}

Shipping City:
{order["shipping_city"]}

Recommended Action:
Review shipment details, verify customer claim, and contact customer within 24 hours.
"""

    return summary.strip()
