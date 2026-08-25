import os
import re
from dotenv import load_dotenv
from google import genai

from tools import (
    lookup_order,
    check_return_eligibility,
    escalate_to_human,
)

from rag import search_policy
from prompts import (
    POLICY_PROMPT,
    CHAT_PROMPT,
    ESCALATION_PROMPT,
)

# ---------------- CONFIG ----------------
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- HELPERS ----------------
def extract_order_id(text):
    match = re.search(r"TR-\d{4}", text.upper())
    return match.group() if match else None


def get_active_order(memory, conversation_state, order_id):
    """Reuse previous order during multi-turn conversation."""
    if order_id:
        return order_id

    if conversation_state.get("active_order"):
        return conversation_state["active_order"]

    return memory.get("last_order_id")


# ---------------- MAIN AGENT ----------------
def get_ai_response(user_message, memory=None, conversation_state=None):

    if memory is None:
        memory = {}

    if conversation_state is None:
        conversation_state = {
            "active_order": None,
            "customer": None,
            "intent": None,
            "eligibility": None,
        }

    memory["logs"] = []

    message = user_message.lower()

    # ======================================================
    # GREETING
    # ======================================================
    greetings = ["hi", "hello", "hey", "hola", "good morning", "good evening"]

    if message.strip() in greetings:
        memory["logs"].append("Planner → Greeting")
        conversation_state["intent"] = "greeting"

        return (
            "Hello! 👋 Welcome to Trendly Support.\n\n"
            "I can help you with:\n"
            "- 📦 Order tracking\n"
            "- ↩️ Returns, exchanges and refunds\n"
            "- 📜 Shipping and refund policies\n"
            "- 👤 Escalating support issues"
        )

    if not message.strip():
        return "Please tell me how I can help you with your Trendly order or policy question."

    if len(message) <= 2 and message not in ["hi", "ok", "no"]:
        return "I didn't understand that. Could you rephrase your question?"

    # ======================================================
    # SAFETY
    # ======================================================
    blocked_keywords = [
        "discount",
        "coupon",
        "promo code",
        "other customer's order",
        "show all orders",
        "internal data",
        "phone number",
        "email address",
        "customer phone",
        "customer email",
    ]

    if any(word in message for word in blocked_keywords):
        return (
            "🔒 I can't provide unauthorized discounts, internal company "
            "information, or another customer's personal data."
        )

    if "invent" in message or "make up" in message:
        return (
            "I can only answer using Trendly's official policy document "
            "and available order information."
        )

    # ======================================================
    # ORDER MEMORY
    # ======================================================
    order_id = extract_order_id(user_message)

    if order_id:
        memory["last_order_id"] = order_id
        conversation_state["active_order"] = order_id

    order_id = get_active_order(memory, conversation_state, order_id)

    # ======================================================
    # RETURN FOLLOW-UP
    # ======================================================
    if (
        ("return it" in message or "exchange it" in message or "refund it" in message)
        and order_id
    ):

        conversation_state["intent"] = "return_request"
        memory["logs"].append("Planner → Return Eligibility Tool")

        result = check_return_eligibility(order_id)
        conversation_state["eligibility"] = result["eligible"]

        if result["eligible"] is True:
            return f"""
## ✅ Return Eligible

**Order ID:** {order_id}

**Item:** {result["item"]}

**Eligibility Reason**

- Delivered {result["days_since_delivery"]} days ago.
- Trendly return window: **30 days**.
- Days remaining: **{result["days_remaining"]}**.

{result["message"]}
"""

        elif result["eligible"] == "exchange_only":
            return f"""
## 🔄 Exchange Available

**Order ID:** {order_id}

{result["message"]}
"""

        return f"""
## ❌ Return Not Eligible

**Order ID:** {order_id}

{result["message"]}
"""

    # ======================================================
    # RETURN / EXCHANGE
    # ======================================================
    if any(word in message for word in ["return", "exchange", "refund"]):

        if not order_id:
            return (
                "Please provide your Order ID (for example: TR-4530) "
                "so I can check your eligibility."
            )

        conversation_state["intent"] = "return_request"
        memory["logs"].append("Planner → Return Eligibility Tool")

        result = check_return_eligibility(order_id)
        conversation_state["eligibility"] = result["eligible"]

        if result["eligible"] is True:
            return f"""
## ✅ Return Request Approved

**Order ID:** {order_id}

**Item:** {result["item"]}

- Delivered {result["days_since_delivery"]} days ago.
- Return window: **30 days**
- Days remaining: **{result["days_remaining"]}**

{result["message"]}

You'll receive return instructions shortly.
"""

        elif result["eligible"] == "exchange_only":
            return f"""
## 🔄 Exchange Available

**Order ID:** {order_id}

{result["message"]}
"""

        return f"""
## ❌ Return / Refund Not Approved

**Order ID:** {order_id}

{result["message"]}
"""

    # ======================================================
    # ESCALATION
    # ======================================================
    escalation_keywords = [
        "damaged",
        "wrong item",
        "wrong size",
        "defective",
        "lost",
        "lost package",
        "lost shipment",
        "missing package",
        "missing parcel",
        "missing delivery",
        "package missing",
        "package not arrived",
        "didn't receive",
        "did not receive",
        "not received",
        "never received",
        "payment failed",
        "payment issue",
        "fraud",
    ]

    if any(word in message for word in escalation_keywords):

        if not order_id:
            return "Please share your Order ID so I can investigate and escalate this issue."

        conversation_state["intent"] = "human_escalation"
        memory["logs"].append("Planner → Human Escalation Tool")

        summary = escalate_to_human(order_id, user_message)

        prompt = ESCALATION_PROMPT.format(
            order_id=order_id,
            issue=user_message,
            summary=summary,
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        return f"""
## 🚨 Escalated to Human Support

**Ticket ID:** ESC-{order_id[-4:]}

**Priority:** High

**Order ID:** {order_id}

**Status:** Escalated

---

### Human Agent Summary

{response.text}

A Trendly support specialist will review your request within **24 hours**.
"""

    # ======================================================
    # ORDER CANCELLATION
    # ======================================================
    if "cancel" in message:

        if not order_id:
            return "Please provide your Order ID so I can check your cancellation request."

        conversation_state["intent"] = "cancel_order"
        memory["logs"].append("Planner → Cancellation Tool")

        order = lookup_order(order_id)

        if not order:
            return "❌ Order not found."

        if order["status"] == "cancelled":
            return f"""
## ✅ Order Already Cancelled

**Order ID:** {order_id}

**Refund Status:** {order.get("refund_status", "Processed")}

No further action is required.
"""

        if order["status"] == "delivered":
            return (
                "This order has already been delivered, so it cannot be cancelled. "
                "If eligible, I can help you start a return or exchange instead."
            )

        return f"""
## Cancellation Request

**Order Status:** {order["status"].replace("_", " ").title()}

Your order has not been delivered yet.

Please contact Trendly support if you'd like to cancel before shipment.
"""

    # ======================================================
    # ORDER LOOKUP
    # ======================================================
    if order_id:

        conversation_state["intent"] = "order_lookup"
        memory["logs"].append("Planner → Order Lookup Tool")

        order = lookup_order(order_id)

        if not order:
            return (
                "❌ I couldn't find an order with that Order ID.\n\n"
                "Please check the Order ID and try again.\n"
                "Trendly Order IDs look like **TR-4521**."
            )

        conversation_state["customer"] = order["customer_name"]
        conversation_state["active_order"] = order["order_id"]

        memory["logs"].append(f"Order Retrieved: {order['order_id']}")
        memory["logs"].append(
            f"Status: {order['status'].replace('_', ' ').title()}"
        )

        status = order["status"].replace("_", " ").title()
        extra_message = ""

        if order["status"] == "delayed":
            extra_message = (
                "⚠️ Your shipment is delayed. "
                "Our logistics team is monitoring it."
            )

        elif order["status"] == "partially_shipped":
            shipped = [
                item["name"] for item in order["items"] if item.get("shipped")
            ]

            pending = [
                f"{item['name']} (ETA: {item.get('backorder_eta', 'TBD')})"
                for item in order["items"]
                if not item.get("shipped")
            ]

            extra_message = (
                f"**Items Shipped:** {', '.join(shipped)}\n\n"
                f"**Items Pending:** {', '.join(pending)}"
            )

        elif order["status"] == "lost_in_transit":
            extra_message = (
                "🚨 This shipment has been marked as Lost in Transit. "
                "I'll help escalate this issue if needed."
            )

        elif order["status"] == "cancelled":
            extra_message = (
                f"**Refund Status:** {order.get('refund_status', 'Processed')}"
            )

        return f"""
## 📦 Order Status

**Order ID:** {order["order_id"]}

**Customer:** {order["customer_name"]}

**Status:** {status}

**Item:** {order["items"][0]["name"]}

**Expected Delivery:** {order["expected_delivery"] or "N/A"}

**Carrier:** {order["carrier"] or "N/A"}

**Shipping City:** {order["shipping_city"]}

---

{extra_message}
"""

    # ======================================================
    # POLICY QUESTIONS (RAG)
    # ======================================================
    policy_keywords = [
        "shipping policy",
        "return policy",
        "refund policy",
        "exchange policy",
        "shipping",
        "refund",
        "returns",
        "delivery",
        "policy",
        "jewellery",
        "jewelry",
    ]

    if any(word in message for word in policy_keywords):

        conversation_state["intent"] = "policy_question"
        memory["logs"].append("Planner → Policy Retrieval (RAG)")

        policy_context = search_policy(user_message)

        if not policy_context.strip():
            return (
                "I couldn't find this information in Trendly's official "
                "policy document, so I can't provide an answer."
            )

        prompt = POLICY_PROMPT.format(
            policy_context=policy_context,
            user_question=user_message,
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        policy_answer = (
            response.text.strip()
            if response and response.text
            else "I couldn't generate a response using Trendly's official policy document."
        )

        return f"""{policy_answer}

---
📚 **Source:** Trendly Policy Document
"""

    # ======================================================
    # GENERAL CHAT
    # ======================================================
    conversation_state["intent"] = "general_chat"
    memory["logs"].append("Planner → General Gemini Chat")

    prompt = CHAT_PROMPT.format(
        chat_history=str(memory),
        user_message=user_message,
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    if response and response.text:
        return response.text

    return "Sorry, I couldn't generate a response. Please try asking again."
