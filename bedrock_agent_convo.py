import streamlit as st
import boto3
import os

st.set_page_config(page_title="Chat with MAJIC")

st.markdown("<h1 style='text-align: center;'>💬 Chat with MAJIC</h1>", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat messages with spacing
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style='margin-top: 1rem; text-align: right;'>
                <div style='display: inline-block; background-color: #e8f5e9; padding: 10px 15px; border-radius: 10px; max-width: 80%;'>
                    <strong>🧑 You:</strong> {msg['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='margin-top: 0.5rem; text-align: left;'>
                <div style='display: inline-block; padding: 10px 15px; border-radius: 10px; max-width: 80%;'>
                    <strong>🤖 Agent:</strong> {msg['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Input and submit button (form)
with st.form("question_form", clear_on_submit=True):
    cols = st.columns([10, 1])
    with cols[0]:
        user_input = st.text_input("Ask something:", placeholder="Type your question...")
    with cols[1]:
        submitted = st.form_submit_button("➤")

# Handle submission
if submitted and user_input.strip():
    query = user_input.strip()

    # Show user's question immediately
    st.session_state.chat_history.append({"role": "user", "content": query})

    # Display loading spinner while waiting
    with st.spinner("🤖 Agent is typing..."):
        # Call Bedrock Agent
        bedrock_agent = boto3.client(
            "bedrock-agent-runtime",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")
        )
        response = bedrock_agent.invoke_agent(
            agentId="XBVIAGTPOF",
            agentAliasId="NBU7DCILKB",
            sessionId="session-1",
            inputText=query,
        )

        full_response = ""
        for event in response["completion"]:
            if "chunk" in event and "bytes" in event["chunk"]:
                full_response += event["chunk"]["bytes"].decode("utf-8")

        # Save agent response
        st.session_state.chat_history.append({"role": "agent", "content": full_response})

    # Rerun to clear input field
    st.rerun()

# Clear conversation button
if st.session_state.chat_history:
    st.markdown("---")
    if st.button("🔄 Clear Conversation"):
        st.session_state.chat_history.clear()
        st.rerun()
