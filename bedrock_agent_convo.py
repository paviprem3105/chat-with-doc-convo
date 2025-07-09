import streamlit as st
import boto3
import os
import uuid

st.set_page_config(page_title="Chat with MAJIC")
st.markdown("<h1 style='text-align: center;'>💬 Chat with MAJIC</h1>", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "loading" not in st.session_state:
    st.session_state.loading = False

# Display chat history
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
                <div style='display: inline-block; padding: 10px 15px; border-radius: 10px; max-width: 80%; background-color: #f1f1f1;'>
                    <strong>🤖 Agent:</strong> {msg['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# Input form
with st.form("question_form", clear_on_submit=True):
    st.markdown("##### Ask something:")
    input_cols = st.columns([10, 1])
    with input_cols[0]:
        user_input = st.text_input(
            label="Your question",
            placeholder="Type your question...",
            key="user_input",
            label_visibility="collapsed",
            disabled=st.session_state.loading
        )
    with input_cols[1]:
        submitted = st.form_submit_button("➤", disabled=st.session_state.loading)

# Handle submission
if submitted and st.session_state.user_input.strip():
    query = st.session_state.user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": query})
    st.session_state.loading = True
    st.rerun()

# Handle agent response
if st.session_state.loading:
    with st.spinner("🤖 Agent is typing..."):
        try:
            bedrock_agent = boto3.client(
                "bedrock-agent-runtime",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")
            )

            response = bedrock_agent.invoke_agent(
                agentId="XBVIAGTPOF",
                agentAliasId="NBU7DCILKB",
                sessionId=st.session_state.session_id,
                inputText=st.session_state.chat_history[-1]["content"],
            )

            full_response = ""
            for event in response["completion"]:
                if "chunk" in event and "bytes" in event["chunk"]:
                    full_response += event["chunk"]["bytes"].decode("utf-8")

        except Exception as e:
            full_response = f"❌ Error: {e}"

        st.session_state.chat_history.append({"role": "agent", "content": full_response})
        st.session_state.loading = False
        st.rerun()

# Clear button
if st.session_state.chat_history:
    st.markdown("---")
    if st.button("🔄 Clear Conversation", disabled=st.session_state.loading):
        st.session_state.chat_history.clear()
        st.rerun()