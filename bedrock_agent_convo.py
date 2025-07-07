import streamlit as st
import boto3

st.set_page_config(page_title="Chat with Documents")

st.markdown("<h1 style='text-align: center;'>💬 Chat with MAJIC</h1>", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Function to handle submission
def submit_question():
    query = st.session_state.user_input.strip()
    if not query:
        return

    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": query})

    # Call Bedrock Agent
    bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="ap-southeast-2")
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

    # Append agent response
    st.session_state.chat_history.append({"role": "agent", "content": full_response})
    st.session_state.user_input = ""  # Clear input

# Show the chat history with styling
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style='text-align: right;'>
                <div style='display: inline-block; background-color: #f0f0f0; padding: 10px 15px; border-radius: 10px; max-width: 80%;'>
                    <strong>🧑 You:</strong> {msg['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align: left;'>
                <strong>🤖 Agent:</strong> {msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

# Input box at the bottom
st.text_input(
    "Ask something:",
    key="user_input",
    on_change=submit_question,
    placeholder="Type your question and press Enter...",
)

# Button to clear conversation
st.markdown("---")
if st.button("🔄 Clear Conversation"):
    st.session_state.chat_history = []
