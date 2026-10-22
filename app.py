import streamlit as st
import anthropic

st.set_page_config(page_title="Friday", page_icon="🤖")
st.title("🤖 Friday")
st.caption("Your AI study and research assistant")

# The API key is read from secrets, never written in the code
try:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
except Exception:
    st.error(
        "API key not found. Add ANTHROPIC_API_KEY in the app's Secrets settings."
    )
    st.stop()

MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 1500

SYSTEM_PROMPT = (
    "Your name is Friday. You are a friendly, clear AI assistant that helps "
    "students with studying and research. Explain things simply, step by step."
)

# Keep the conversation so Friday remembers earlier messages
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar: clear chat button
with st.sidebar:
    if st.button("🗑️ Clear chat"):
        st.session_state.history = []
        st.rerun()

# Show previous messages
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


def stream_answer():
    """Yield Friday's reply piece by piece so it appears as it is written."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=st.session_state.history,
    ) as stream:
        for text in stream.text_stream:
            yield text


# Chat box at the bottom
question = st.chat_input("Ask Friday anything...")

if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(stream_answer())
            st.session_state.history.append({"role": "assistant", "content": answer})
        except anthropic.AuthenticationError:
            st.session_state.history.pop()
            st.error("Your API key is invalid. Please check your Secrets.")
        except anthropic.RateLimitError:
            st.session_state.history.pop()
            st.error("Too many requests right now. Wait a moment and try again.")
        except anthropic.APIConnectionError:
            st.session_state.history.pop()
            st.error("Can't reach the server. Check your internet connection.")
        except anthropic.APIError as e:
            st.session_state.history.pop()
            st.error(f"Sorry, something went wrong: {e}")
