# SOLUTION.md

# Trendly AI Support Assistant — Solution Note

## Overview

Trendly receives around 2,000 customer support chats daily, most of which involve repetitive workflows such as order tracking, returns, exchanges, refunds, and shipping questions.

This solution uses a lightweight AI orchestration layer that combines deterministic tools with Gemini and RAG instead of relying on keyword matching or a single LLM prompt.

---

# Architecture

## High-Level Flow

```text
Customer
      │
      ▼
 Streamlit Chat UI
      │
      ▼
  agent.py (Planner)
      │
      ├──────── lookup_order()
      │
      ├──────── check_return_eligibility()
      │
      ├──────── escalate_to_human()
      │
      └──────── search_policy() (RAG)
                      │
                      ▼
              Gemini 3.6 Flash
                      │
                      ▼
               Final Response
```

---

# Components

## 1. Streamlit Frontend

Provides a conversational interface using Streamlit's chat components.

Responsibilities:

* Maintain chat history.
* Display assistant responses.
* Send user messages to the planner.

---

## 2. Planner (agent.py)

Acts as the orchestration layer.

Responsibilities:

* Detect customer intent.
* Decide which tool should run.
* Maintain short-term conversation memory.
* Call Gemini only when reasoning or policy explanation is needed.

---

## 3. Tools

### lookup_order()

Retrieves order information from `orders.json`.

### check_return_eligibility()

Combines:

* Order status.
* Delivery date.
* Final Sale flag.
* Product category.
* Trendly return rules.

### escalate_to_human()

Creates a structured escalation summary including:

* Order ID.
* Customer issue.
* Current status.
* Suggested next action.

---

## 4. Retrieval-Augmented Generation

Policy questions use LangChain retrieval over `trendly_policy.md`.

Benefits:

* No hardcoded policy responses.
* Reduced hallucinations.
* Single source of truth.

---

# Design Decisions

## Why Tool Calling?

Order status and return eligibility are deterministic.

Using tools ensures:

* Accurate order information.
* Correct policy application.
* No fabricated tracking information.

## Why RAG?

Policies may change independently of application logic.

RAG allows:

* Easy policy updates.
* Grounded answers.
* Lower hallucination risk.

## Why Streamlit?

Chosen for simplicity and rapid deployment while still supporting multi-turn conversations and a live public demo.

---

# Edge Cases Handled

* Delayed shipment acknowledgement.
* Partial shipment explanation.
* Lost shipment escalation.
* Cancelled order already refunded.
* Jewellery non-returnable.
* Final Sale exchange-only.
* Return window exceeded.
* Missing Order ID.
* Privacy requests refused.
* Unauthorized discount requests refused.
* Invented policy requests refused.

---

# Known Limitations

* Uses a fixed dataset (`orders.json`) instead of a live database.
* Human escalation generates a summary rather than creating a real support ticket.
* Conversation memory is session-based and not persisted across browser refreshes.
* Authentication is not implemented because it is outside the assignment scope.

---

# Trade-offs

| Decision                      | Reason                                    |
| ----------------------------- | ----------------------------------------- |
| Tool-first architecture       | Improves reliability over pure prompting. |
| RAG only for policy questions | Keeps retrieval focused and inexpensive.  |
| Streamlit frontend            | Faster deployment and easier evaluation.  |

---

# Five Discovery Questions for Trendly Operations Team

1. What information is required before creating a real return or exchange request?
2. Which order statuses should automatically escalate instead of remaining AI-handled?
3. Should VIP customers receive different refund or escalation workflows?
4. What SLA should the assistant communicate for damaged or lost parcel escalations?
5. Should exchange inventory availability be checked before approving an exchange?

---

# Future Improvements

* Connect to a live order database.
* Create real support tickets through a CRM API.
* Add customer authentication before exposing order information.
* Add shipment tracking API integration.
* Persist conversation history across sessions.
