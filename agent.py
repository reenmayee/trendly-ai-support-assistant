import os
import re
from dotenv import load_dotenv
from google import genai

from tools import (
    lookup_order,
    check_return_eligibility,
    escalate_to_human
)
from rag import search_policy

from prompts import (
    SYSTEM_PROMPT,
    POLICY_PROMPT,
    CHAT_PROMPT
)

# ---------------- CONFIG ----------------
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_ai_response(user_message, chat_history=None):
    """Main planner for Trendly AI Support Assistant."""

    # ---------------- MEMORY ----------------
    if chat_history is None:
        chat_history = {}

    # Planner logs (for orchestration/debugging)
    chat_history["logs"] = []

    message = user_message.lower()

    # ---------------- SAFETY GUARDRAILS ----------------
    if "make up" in message or "invent" in message:
        return (
            "❌ I can't invent or modify Trendly policies. "
            "I can only answer using Trendly's official policy document."
        )

    if "discount" in message or "90%" in message:
        return (
            "I'm sorry, but I can't provide unauthorized discounts. "
            "I can help with orders, returns, exchanges, refunds, and shipping policies."
        )

    private_keywords = [
        "phone number",
        "email address",
        "customer phone",
        "customer email",
        "marcus bell phone",
        "ananya rao phone",
        "priya nair phone",
        "diego ramos phone"
    ]

    if any(word in message for word in private_keywords):
        return "🔒 I can't share another customer's personal information."

    # ---------------- ORDER ID EXTRACTION ----------------
    match = re.search(r"TR-\d{4}", user_message.upper())

    order_id = None
    if match:
        order_id = match.group()
        chat_history["last_order_id"] = order_id

    # ============================================================
    # PLANNER ROUTE 1 — FOLLOW-UP MEMORY
    # ============================================================
    if ("return it" in message or "exchange it" in message) and not order_id:

        last_order = chat_history.get("last_order_id")

        if not last_order:
            return "Please provide your Order ID first."

        chat_history["logs"].append("Planner → Return Eligibility Tool")

        result = check_return_eligibility(last_order)

        if result["eligible"] is True:
            return f"""
## Return Request Approved ✅

**Order ID:** {last_order}

**Item:** {result["item"]}

{result["message"]}

You'll receive return instructions shortly.
"""

        elif result["eligible"] == "exchange_only":
            return f"""
## Exchange Available ✅

**Order ID:** {last_order}

{result["message"]}

If you'd like to exchange this item, our support team will guide you through the process.
"""

        else:
            return f"""
## Return Request Not Approved ❌

{result["message"]}
"""

    # ============================================================
    # PLANNER ROUTE 2 — POLICY QUESTIONS (NO ORDER REQUIRED)
    # ============================================================
    policy_only_questions = [
        "return policy",
        "refund policy",
        "shipping policy",
        "exchange policy",
        "can i return jewellery",
        "can i return jewelry",
        "can i exchange jewellery",
        "can i exchange jewelry"
    ]

    if any(q in message for q in policy_only_questions):

        chat_history["logs"].append("Planner → Policy Retrieval (RAG)")

        policy_context = search_policy(user_message)

        prompt = POLICY_PROMPT.format(
            system_prompt=SYSTEM_PROMPT,
            policy_context=policy_context,
            user_question=user_message
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    # ============================================================
    # PLANNER ROUTE 3 — RETURN / EXCHANGE / REFUND TOOL
    # ============================================================
    return_keywords = ["return", "exchange", "refund"]

    if any(word in message for word in return_keywords):

        if not order_id:
            return (
                "Please provide your Order ID "
                "(for example: TR-4530) so I can check eligibility."
            )

        chat_history["logs"].append("Planner → Return Eligibility Tool")

        result = check_return_eligibility(order_id)

        if result["eligible"] is True:
            return f"""
## Return Request Approved ✅

**Order ID:** {result["order_id"]}

**Item:** {result["item"]}

{result["message"]}

You'll receive return instructions shortly.
"""

        elif result["eligible"] == "exchange_only":
            return f"""
## Exchange Available ✅

**Order ID:** {order_id}

{result["message"]}

This item isn't eligible for a refund, but it **can be exchanged** according to Trendly's policy.
"""

        else:
            return f"""
## Return / Refund Request Not Approved ❌

{result["message"]}
"""

    # ============================================================
    # PLANNER ROUTE 4 — HUMAN ESCALATION TOOL
    # ============================================================
    escalation_keywords = [
        "damaged",
        "wrong item",
        "wrong size",
        "received wrong size",
        "received wrong item",
        "defective",
        "lost",
        "missing package",
        "missing parcel",
        "package not arrived",
        "not delivered"
    ]

    if any(word in message for word in escalation_keywords):

        if not order_id:
            return (
                "Please share your Order ID so I can investigate and escalate this issue."
            )

        chat_history["logs"].append("Planner → Human Escalation Tool")

        summary = escalate_to_human(order_id, user_message)

        return f"""
## Escalated to Human Support 🚨

I'm sorry you're facing this issue.

Your request has been forwarded to a human support specialist.

### Support Ticket

**Order ID:** {order_id}

**Issue:** {user_message}

**Status:** Escalated

**Next Step:** A support specialist will review your request within **24 hours**.

### Internal Summary

{summary}
"""

    # ============================================================
    # PLANNER ROUTE 5 — CANCELLATION
    # ============================================================
    if "cancel" in message:

        if not order_id:
            return "Please provide your Order ID so I can check your cancellation request."

        chat_history["logs"].append("Planner → Cancellation Check")

        order = lookup_order(order_id)

        if not order:
            return "❌ Order not found."

        if order["status"] == "cancelled":
            return f"""
## Order Already Cancelled ✅

**Order ID:** {order_id}

Your order has already been cancelled.

**Refund Status:** {order.get("refund_status", "Processed")}

No further action is required.
"""

        if order["status"] == "delivered":
            return (
                "This order has already been delivered, so it can't be cancelled. "
                "If it's eligible, I can help you request a return or exchange instead."
            )

        return (
            f"Your order is currently **{order['status'].replace('_', ' ').title()}**.\n\n"
            "Please contact support if you'd like to cancel it before shipment."
        )

    # ============================================================
    # PLANNER ROUTE 6 — ORDER LOOKUP TOOL
    # ============================================================
    if order_id:

        chat_history["logs"].append("Planner → Order Lookup Tool")

        order = lookup_order(order_id)

        if not order:
            return "❌ I couldn't find an order with that Order ID."

        status = order["status"].replace("_", " ").title()

        extra_message = ""

        if order["status"] == "delayed":
            extra_message = (
                "\n\n⚠️ We're sorry your shipment is delayed. "
                "Our logistics team is actively monitoring it."
            )

        elif order["status"] == "partially_shipped":

            shipped_items = []
            pending_items = []

            for item in order["items"]:
                if item.get("shipped"):
                    shipped_items.append(item["name"])
                else:
                    pending_items.append(
                        f"{item['name']} (ETA: {item.get('backorder_eta', 'TBD')})"
                    )

            extra_message = (
                f"\n\n**Items Shipped:** {', '.join(shipped_items)}"
                f"\n\n**Items Pending:** {', '.join(pending_items)}"
            )

        elif order["status"] == "lost_in_transit":
            extra_message = (
                "\n\n🚨 This shipment has been marked as **Lost in Transit**. "
                "I'll help escalate this issue to our support team."
            )

        elif order["status"] == "cancelled":
            extra_message = (
                f"\n\n**Refund Status:** {order.get('refund_status', 'Processed')}"
            )

        return f"""
## Order Status 📦

**Order ID:** {order["order_id"]}

**Status:** {status}

**Item:** {order["items"][0]["name"]}

**Expected Delivery:** {order["expected_delivery"] or "N/A"}

**Carrier:** {order["carrier"] or "N/A"}

**Shipping City:** {order["shipping_city"]}

{extra_message}
"""

    # ============================================================
    # PLANNER ROUTE 7 — GENERAL POLICY QUESTIONS (RAG)
    # ============================================================
    policy_keywords = [
        "shipping",
        "refund",
        "refunds",
        "return policy",
        "returns",
        "exchange policy",
        "delivery",
        "policy"
    ]

    if any(word in message for word in policy_keywords):

        chat_history["logs"].append("Planner → Policy Retrieval (RAG)")

        policy_context = search_policy(user_message)

        prompt = POLICY_PROMPT.format(
            system_prompt=SYSTEM_PROMPT,
            policy_context=policy_context,
            user_question=user_message
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    # ============================================================
    # PLANNER ROUTE 8 — GENERAL GEMINI CHAT
    # ============================================================
    chat_history["logs"].append("Planner → General Gemini Chat")

    prompt = CHAT_PROMPT.format(
        system_prompt=SYSTEM_PROMPT,
        chat_history=str(chat_history),
        user_message=user_message
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text
