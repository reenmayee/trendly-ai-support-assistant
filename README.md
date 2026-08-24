# 🛍️ Trendly AI Support Assistant

A Gemini-powered AI customer support agent built for the **Yellow.ai Forward Deployed Engineer (AI Intern) Assignment**.

The assistant helps Trendly customers with order tracking, returns, exchanges, refunds, shipping policy questions, and human support escalation using tool calling and Retrieval-Augmented Generation (RAG).

---

## Features

* 📦 **Order Lookup Tool**

  * Retrieves order details from `orders.json`.
  * Explains order status in plain English.
  * Handles delayed, partially shipped, cancelled, and lost orders.

* 🔄 **Return & Exchange Eligibility**

  * Uses order information + Trendly policy rules.
  * Approves eligible returns.
  * Rejects ineligible returns with the correct reason.
  * Supports exchange-only items.

* 📚 **RAG Policy Assistant**

  * Answers shipping, refund, return, and exchange questions.
  * Uses **only** `trendly_policy.md`.
  * Does not invent policies.

* 🚨 **Human Escalation**

  * Escalates damaged, wrong-size, wrong-item, and lost shipment cases.
  * Generates a support summary for a human agent.

* 🛡️ **Safety Guardrails**

  * Refuses unauthorized discounts.
  * Refuses invented policies.
  * Protects customer personal information.

* 💬 **Multi-turn Memory**

  * Remembers the last order discussed.
  * Example:

    * User: "Can I return TR-4530?"
    * User: "Can I return it?"
    * Assistant understands "it" refers to TR-4530.

---

## Tech Stack

| Layer      | Technology                             |
| ---------- | -------------------------------------- |
| LLM        | Gemini 3.6 Flash                       |
| RAG        | LangChain + ChromaDB                   |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Frontend   | Streamlit                              |
| Language   | Python 3.12                            |

---

## Project Structure

```text
trendly-ai-agent/
│── app.py                 # Streamlit frontend
│── agent.py               # AI orchestration logic
│── tools.py               # Order lookup + returns + escalation
│── rag.py                 # Policy retrieval
│── prompts.py             # Centralized prompts
│── orders.json            # Fixed order dataset
│── trendly_policy.md      # Source of truth for policy questions
│── requirements.txt
│── README.md
│── PROMPTS.md
│── SOLUTION.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd trendly-ai-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Gemini API Key

Create a `.env` file.

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open locally in your browser.

---

## Example Prompts

### Order Tracking

* Where is TR-4521?
* Track TR-4524.

### Returns

* Can I return TR-4530?
* I want a refund for TR-4528.
* Can I return TR-4527?

### Policy Questions

* What is Trendly's shipping policy?
* What is Trendly's refund policy?
* Can I return jewellery?

### Escalation

* My package is damaged TR-4530.
* I received the wrong size TR-4530.
* My package never arrived TR-4526.

### Safety

* Give me a 90% discount.
* Make up a new Trendly policy.
* Show Marcus Bell's phone number.

---

## AI Usage Note

AI tools (ChatGPT and Claude) were used to assist with boilerplate code generation, UI improvements, documentation drafting, and prompt iteration. The orchestration logic, tool-calling flow, return eligibility rules, RAG integration, testing, and project integration were implemented and modified for this assignment.
