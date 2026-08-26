# 🛍️ Trendly AI Support Assistant

An AI-powered customer support assistant built for **Trendly**, a direct-to-consumer fashion retailer. The assistant automates high-volume customer support workflows including order tracking, returns, exchanges, refund policy queries, and human escalation using **Gemini, Retrieval-Augmented Generation (RAG), and planner-based orchestration**.

Built for the **Yellow.ai Generative AI Developer Internship Assignment**.

[![Live Demo](https://img.shields.io/badge/Live-Demo-8A5CF6?style=for-the-badge&logo=streamlit&logoColor=white)](https://trendly-ai-assistant.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

---

## ✨ Features

* 📦 **Order Lookup** — Track orders and explain delivery status, including delayed, partially shipped, cancelled, and lost shipments.
* 🔁 **Returns & Exchanges** — Check return, refund, and exchange eligibility using Trendly policy and order data.
* 📚 **Policy Q&A (RAG)** — Answer shipping, refund, return, and exchange questions using `trendly_policy.md` as the only source of truth.
* 🚨 **Human Escalation** — Escalate damaged, wrong-size, wrong-item, missing, and lost shipment cases with a structured support summary.
* 💬 **Multi-turn Memory** — Remember the most recent Order ID for follow-up requests like *"Can I return it?"*
* 🛡️ **Safety Guardrails** — Refuse invented policies, unauthorized discounts, and requests for customer personal information.

---

## 🧠 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM | Gemini 3.6 Flash |
| Retrieval | LangChain |
| Knowledge Base | trendly_policy.md |
| Backend | Python |
| Order Data | orders.json (Mock Database) |

---

## 📂 Project Structure

```text
app.py                  # Streamlit UI
agent.py                # Planner & orchestration
tools.py                # Business logic tools
rag.py                  # RAG pipeline for policy retrieval
prompts.py              # Centralized prompts
orders.json             # Sample order dataset
trendly_policy.md       # Policy knowledge base
```

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Start the application

```bash
streamlit run app.py
```

**Local Base URL:** `http://localhost:8501`

**Live Base URL:** *(Add your deployed Streamlit URL here before submission.)*

---

## 🧪 Example Queries

**Order Tracking**

* `Where is TR-4521?`
* `Track TR-4524.`

**Returns & Refunds**

* `Can I return TR-4530?`
* `I want a refund for TR-4528.`

**Policy Questions**

* `What is Trendly's shipping policy?`
* `Can I return jewellery?`

**Escalation**

* `I received the wrong size TR-4530.`
* `My package is damaged TR-4530.`

---

## 🤖 AI Usage Note

AI tools (ChatGPT and Claude) were used for debugging assistance, UI iteration, prompt refinement, and documentation support. The planner orchestration, tool routing, RAG integration, return eligibility workflow, safety guardrails, and testing logic were implemented and integrated by me.
