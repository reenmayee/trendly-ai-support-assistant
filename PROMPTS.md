# PROMPTS.md

# Prompt Engineering

This document describes the prompts used in the Trendly AI Support Assistant and how they were refined during development to improve accuracy, consistency, and safety.

---

## SYSTEM_PROMPT

**Purpose**

Defines the assistant's identity and behavior across every conversation.

**Responsibilities**

* Act as Trendly's AI customer support assistant.
* Keep responses concise, polite, and customer-friendly.
* Never invent Trendly policies.
* Never expose customer personal information.
* Never provide unauthorized discounts or promotions.
* Use tool outputs whenever available instead of guessing.

**Why this prompt exists**

A single reusable system prompt keeps the assistant's behavior consistent across all workflows.

---

## POLICY_PROMPT

**Purpose**

Used only for shipping, return, refund, and exchange policy questions.

**Inputs**

* Retrieved context from `trendly_policy.md`.
* Customer's question.

**Prompt Behavior**

* Answer only from the provided policy context.
* Do not use outside knowledge.
* If the answer is not present in the policy, clearly say so instead of making one up.

**Reasoning**

This prompt grounds Gemini's responses in Trendly's official policy document and reduces hallucinations.

---

## CHAT_PROMPT

**Purpose**

Handles conversations that do not require policy retrieval or backend tools.

**Examples**

* Greetings.
* Thank-you messages.
* General shopping assistance.

**Behavior**

Uses the conversation history to produce natural responses while following the rules defined in `SYSTEM_PROMPT`.

---

## Prompt Iterations

### Iteration 1 — Single Prompt

Initially, one prompt handled every conversation.

**Issue:** Policy questions sometimes relied on Gemini's general knowledge instead of the provided document.

### Iteration 2 — Dedicated Policy Prompt

A separate `POLICY_PROMPT` was introduced for RAG-based policy questions.

**Improvement:** Policy responses became grounded in `trendly_policy.md` only.

### Iteration 3 — Safety Refinements

The system prompt was updated to explicitly refuse:

* Invented Trendly policies.
* Unauthorized discounts.
* Requests for another customer's phone number or email address.

**Improvement:** Reduced hallucinations and ensured consistent safety behavior across conversations.
