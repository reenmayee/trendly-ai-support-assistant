import streamlit as st
from agent import get_ai_response

st.set_page_config(
    page_title="Trendly AI Support Assistant",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Trendly AI Support Assistant")
st.caption("Your AI-powered customer support agent for orders, returns, exchanges and policy questions.")

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
        st.rerun()

    st.markdown("### Agent Activity")
    if "logs" in st.session_state:
        for log in st.session_state.logs:
            st.success(log)

# Chat history (only for UI)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Memory (only for agent state)
if "memory" not in st.session_state:
    st.session_state.memory = {}

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask me about your order, refund, or Trendly policy...")

if user_input:
    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Send MEMORY to the agent (not messages)
    with st.spinner("Checking your request..."):
        response = get_ai_response(user_input, st.session_state.memory)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):

        # Show badge only for policy/RAG answers
        policy_keywords = ["refund", "shipping", "return policy", "exchange policy", "policy"]

        if any(word in user_input.lower() for word in policy_keywords):
            st.markdown("""
            <div style="
                background:#F4EDFF;
                border-left:4px solid #A78BFA;
                padding:12px;
                border-radius:10px;
                margin-bottom:12px;">
                <b>📚 Policy Grounded</b><br>
                <span style="color:#666;">Source: trendly_policy.md</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(response)