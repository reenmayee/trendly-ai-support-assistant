# 🛍️ Trendly AI Support Assistant

An AI-powered customer support agent built for **Trendly**, a direct-to-consumer fashion retailer, to automate high-volume customer support conversations using **LLMs, RAG, tool orchestration, and prompt engineering**.

This project was built as part of the **Yellow.ai Generative AI Developer Internship assignment**, with a focus on building a reliable conversational AI system rather than a simple chatbot.

---

## ✨ Overview

Trendly receives thousands of customer support chats every day. Around **70%** of these conversations are repetitive:

* Order tracking
* Returns & exchanges
* Refund eligibility
* Shipping and refund policy questions

This assistant automates those workflows end-to-end while safely escalating unsupported cases to a human support specialist.

The agent combines deterministic Python tools with Gemini for grounded natural-language responses.

---

## 🚀 Features

### 📦 Order Lookup

* Track orders using an Order ID (e.g. `TR-4521`).
* Explain order status in customer-friendly language.
* Handles edge cases including:

  * In Transit
  * Delivered
  * Delayed Shipment
  * Partially Shipped
  * Lost in Transit
  * Cancelled Orders

### 🔁 Returns & Exchanges

* Checks eligibility using both **order data** and **Trendly policy**.
* Enforces:

  * 30-day return window.
  * Jewellery non-returnable policy.
  * Final Sale exchange-only policy.
  * Cancelled orders cannot be returned.
  * Lost shipments are escalated instead of returned.

### 📚 Policy Question Answering (RAG)

* Answers shipping, refund, return, and exchange policy questions.
* Uses **Retrieval-Augmented Generation (RAG)** over `trendly_policy.md`.
* Does **not** answer from model memory.
* Refuses to invent policies if information is unavailable.

### 🚨 Human Escalation

Automatically escalates issues such as:

* Wrong item received.
* Wrong size received.
* Damaged product.
* Defective product.
* Lost shipment.
* Missing package.

Generates a structured support ticket with issue summary and next steps.

### 🛡️ Safety Guardrails

The assistant refuses:

* Invented Trendly policies.
* Unauthorized discounts or promotions.
* Customer phone numbers or email addresses.
* Requests that expose another customer's information.

### 💬 Multi-turn Conversation Memory

The assistant remembers the most recent Order ID during a session.

Example:

> **User:** Where is TR-4530?

> **Assistant:** Order details...

> **User:** Can I return it?

The assistant correctly resolves **"it"** as **TR-4530**.

---

## 🧠 Architecture

The assistant uses a planner-based orchestration approach.

```text
                User Query
                     │
                     ▼
           Planner (agent.py)
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 Order Lookup    Policy RAG    Return Tool
   (tools.py)      (rag.py)     (tools.py)
      │              │              │
      └──────────────┼──────────────┘
                     ▼
          Human Escalation Tool
                     │
                     ▼
          Gemini Response Generation
                     │
                     ▼
               Streamlit UI
```

### Planner Responsibilities

The planner (`agent.py`) routes each user request to the appropriate tool:

| User Intent                | Planner Route           |
| -------------------------- | ----------------------- |
| Track an order             | Order Lookup Tool       |
| Return / Refund / Exchange | Return Eligibility Tool |
| Shipping / Refund Policy   | RAG Policy Retrieval    |
| Damaged / Wrong Item       | Human Escalation Tool   |
| Greetings / General Chat   | Gemini Chat Prompt      |

This keeps business logic deterministic while using the LLM only where language generation is needed.

---

## 🛠️ Tech Stack

| Component        | Technology                        |
| ---------------- | --------------------------------- |
| Frontend         | Streamlit                         |
| LLM              | Google Gemini 3.6 Flash           |
| Retrieval        | LangChain + ChromaDB              |
| Embeddings       | HuggingFace Sentence Transformers |
| Backend          | Python                            |
| Knowledge Source | `trendly_policy.md`               |
| Order Database   | `orders.json`                     |

---

## 📂 Project Structure

```text
trendly-ai-support-assistant/
│
├── app.py                  # Streamlit UI
├── agent.py                # Planner & orchestration
├── tools.py                # Business logic tools
├── rag.py                  # Policy retrieval pipeline
├── prompts.py              # Centralized prompts
│
├── orders.json             # Sample order database
├── trendly_policy.md       # Policy knowledge base
│
├── README.md
├── PROMPTS.md
├── SOLUTION.md
├── requirements.txt
└── .gitignore
```

---

## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/reenmayee/trendly-ai-support-assistant.git
cd trendly-ai-support-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 4. Run the application

```bash
streamlit run app.py
```

The application runs at:

```text
http://localhost:8501
```

---

## 🧪 Example Test Prompts

### Order Tracking

* Where is TR-4521?
* Track TR-4524.
* Where is TR-4526?

### Returns & Refunds

* Can I return TR-4530?
* I want a refund for TR-4528.
* Can I return TR-4527?

### Policy Questions

* What is Trendly's shipping policy?
* What is Trendly's refund policy?
* Can I return jewellery?

### Escalation

* I received the wrong size TR-4530.
* My package is damaged TR-4530.
* My parcel never arrived TR-4526.

### Safety

* Give me a 90% discount.
* Make up a new return policy.
* Show Marcus Bell's phone number.

---

## 🔒 Guardrails

The assistant is intentionally designed to avoid hallucinations and unsafe responses.

Implemented protections include:

* Policy responses are grounded only in `trendly_policy.md`.
* Return eligibility is computed through Python tools instead of the LLM.
* Personally identifiable information is never exposed.
* Unsupported policy requests return an explicit refusal instead of fabricated information.

---

## 📈 Edge Cases Covered

* Delivered outside return window.
* Final Sale products.
* Jewellery returns.
* Cancelled orders.
* Lost shipments.
* Delayed shipments.
* Partial shipment with pending items.
* Missing Order ID.
* Invalid Order ID.
* Multi-turn follow-up requests.

---

## 🤖 AI Usage Note

AI tools were used as development assistants during this project.

**AI-assisted tasks**

* UI iteration and Streamlit layout improvements.
* Prompt drafting and refinement.
* Code review and debugging assistance.
* Documentation drafting.

**Implemented and integrated by me**

* Planner-based orchestration (`agent.py`).
* Tool routing logic.
* Return eligibility workflow.
* RAG integration with Trendly policy.
* Safety guardrails and refusal logic.
* Multi-turn conversation memory.
* End-to-end testing across assignment scenarios.

---

## 📌 Known Limitations

* Uses a fixed dataset of 10 sample orders.
* Human escalation creates a support summary instead of integrating with a ticketing system.
* Conversation memory persists only within a Streamlit session.
* No authentication or real order management API integration.

---

## 👩‍💻 Author

**Reenmayee Panda**

Built as a submission for the **Yellow.ai Generative AI Developer Internship Assignment**.
