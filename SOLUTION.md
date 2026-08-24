# Trendly AI Support Assistant — Solution Note

## Overview

The goal of this project was to build an AI customer support assistant for **Trendly** that can automate repetitive support conversations while safely handing complex issues to a human support team.

Instead of relying entirely on an LLM, I used a **planner-based architecture** that routes user requests to deterministic Python tools for business logic and uses Gemini only for grounded natural language generation. This improves reliability for workflows like returns, order tracking, and policy questions.

---

## Architecture

The application is divided into four main components:

### 1. Planner (`agent.py`)

The planner is responsible for identifying the user's intent and deciding which workflow should execute.

It routes requests to:

* Order Lookup Tool
* Return / Exchange Eligibility Tool
* Policy Retrieval (RAG)
* Human Escalation Tool
* General Chat (Gemini)

This orchestration keeps business decisions outside the LLM wherever possible.

### 2. Business Logic (`tools.py`)

All deterministic workflows are implemented as Python tools.

Implemented tools include:

* Order lookup using `orders.json`.
* Return and exchange eligibility.
* Human escalation summary generation.

This ensures policy rules are enforced consistently without depending on model reasoning.

### 3. Retrieval-Augmented Generation (`rag.py`)

Policy questions are answered using **RAG** over `trendly_policy.md`.

The assistant retrieves the relevant policy section and passes only that context to Gemini, ensuring responses remain grounded in Trendly's official policy.

### 4. Prompt Layer (`prompts.py`)

Prompts are centralized and separated by responsibility:

* `SYSTEM_PROMPT`
* `POLICY_PROMPT`
* `CHAT_PROMPT`

This keeps prompt engineering independent from application logic and makes prompts easier to maintain.

---

## Key Design Trade-offs

### Planner + Tools vs LLM-only Reasoning

I chose to implement order lookup, return eligibility, and escalation as deterministic Python tools rather than asking the LLM to interpret raw order data.

**Benefit:** predictable decisions, easier debugging, and fewer hallucinations.

### RAG for Policy Questions

Instead of hardcoding policy responses, the assistant retrieves information from the provided policy document.

**Benefit:** policy updates only require updating `trendly_policy.md` instead of changing prompts or code.

### Human Escalation

Issues like damaged items, wrong size, and lost shipments are escalated immediately instead of attempting an automated resolution.

**Benefit:** creates a clean handoff between AI automation and human support.

---

## Safety & Guardrails

The assistant includes deterministic safety checks before calling Gemini.

Implemented protections include:

* Refusing invented Trendly policies.
* Refusing unauthorized discounts or promotions.
* Refusing requests for customer phone numbers or email addresses.
* Using the policy document as the only source of truth for policy-related questions.

These guardrails reduce hallucinations and prevent sensitive information leakage.

---

## Known Limitations

* The project uses the provided sample dataset (`orders.json`) instead of a live order management system.
* Conversation memory is session-based within Streamlit and does not persist across user sessions.
* Human escalation generates a structured summary but is not connected to a real ticketing platform.
* The assistant supports English only.

---

## Discovery Questions for Trendly's Operations Team

Before building this for production, I would ask:

1. Which customer issues must always be escalated instead of being handled automatically?
2. Are there exceptions to the standard return policy for premium customers or promotional campaigns?
3. Which ticketing or CRM platform should escalation integrate with (Zendesk, Freshdesk, Salesforce, etc.)?
4. Should conversation history persist across customer accounts instead of only the current session?
5. What customer support metrics (resolution rate, escalation rate, CSAT, response time) should the assistant optimize for?

---

## Testing Summary

The assistant was tested across the core scenarios described in the assignment:

* Order lookup across different order statuses.
* Return, refund, and exchange eligibility.
* Policy questions grounded using RAG.
* Human escalation scenarios.
* Multi-turn follow-up conversations.
* Safety and refusal cases to verify hallucination prevention.

This implementation focuses on reliable orchestration, grounded responses, and clear separation between business logic and LLM-generated language.
