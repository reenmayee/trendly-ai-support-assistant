import streamlit as st
from agent import get_ai_response

st.set_page_config(
    page_title="Trendly AI Support Assistant",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Trendly AI Support Assistant")
st.caption("Your AI-powered customer support agent for orders, returns, exchanges and policy questions.")

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = {}

# NEW: Multi-turn conversation memory
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = {
        "active_order": None,
        "customer": None,
        "intent": None,
        "eligibility": None
    }

if "logs" not in st.session_state:
    st.session_state.logs = []

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("🛍️ Trendly AI Assistant")

    st.markdown("### Try these prompts")

    st.markdown("""
    **📦 Order Tracking**
    - Where is TR-4521?
    - Track TR-4524.

    **↩️ Returns & Refunds**
    - Can I return TR-4530?
    - I want a refund for TR-4528.

    **📜 Policies**
    - What is Trendly's shipping policy?
    - Can I return jewellery?

    **🚨 Escalation**
    - My package is damaged TR-4530.
    """)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.memory = {}
        st.session_state.conversation_state = {
            "active_order": None,
            "customer": None,
            "intent": None,
            "eligibility": None
        }
        st.session_state.logs = []
        st.rerun()

    st.markdown("---")
    st.markdown("### Current Conversation")

    if st.session_state.conversation_state["active_order"]:
        st.info(
            f"**Active Order:** {st.session_state.conversation_state['active_order']}"
        )

    if st.session_state.conversation_state["intent"]:
        st.success(
            f"**Intent:** {st.session_state.conversation_state['intent']}"
        )

    st.markdown("---")
    st.markdown("### Agent Activity")

    if st.session_state.logs:
        for log in st.session_state.logs[-5:]:
            st.success(log)
    else:
        st.caption("No tools executed yet.")

# ---------------- Display Chat ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- Chat Input ----------------
user_input = st.chat_input(
    "Ask me about your order, refund, or Trendly policy..."
)

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Spinner while tools run
    with st.spinner("Checking your request against Trendly orders and policy..."):
        response = get_ai_response(
            user_input,
            st.session_state.memory,
            st.session_state.conversation_state
        )
        # Update sidebar logs from agent memory
        st.session_state.logs = st.session_state.memory.get("logs", [])

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):

        # Policy grounded badge
        policy_keywords = [
            "refund",
            "shipping",
            "return policy",
            "exchange policy",
            "policy"
        ]

        if any(word in user_input.lower() for word in policy_keywords):
            st.markdown("""
            <div style="
                background:#F4EDFF;
                border-left:4px solid #8B5CF6;
                padding:12px;
                border-radius:10px;
                margin-bottom:12px;">
                <b>📚 Policy Grounded Response</b><br>
                <span style="color:#555;">
                Source: trendly_policy.md (official Trendly policy)
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Escalation ticket styling
        if "ESC-" in response:
            st.markdown(f"""
            <div style="
                background:#FFF7ED;
                border:1px solid #FB923C;
                padding:15px;
                border-radius:12px;
                margin-bottom:15px;">
                <h4 style="color:#EA580C;margin:0;">
                    👤 Escalated to Human Support
                </h4>
                <p style="margin-top:8px;">
                    A support ticket has been created for this request.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(response)
