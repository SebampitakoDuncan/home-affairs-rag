import streamlit as st

st.set_page_config(page_title="Home Affairs RAG", page_icon="🏠", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    .stApp, .stMarkdown, .stTextInput, .stChatInput, .stChatMessage {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    * { font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🏠 Home Affairs RAG System")
st.markdown("Ask questions about Australian visas, citizenship, and immigration.")

openrouter_key = st.sidebar.text_input("OpenRouter API Key", type="password")
openrouter_model = st.sidebar.text_input("Model", value="gpt-4o-mini")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your question about Australian visas..."):
    if not openrouter_key:
        st.error("Please set OPENROUTER_API_KEY in Settings")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.info(
                "Configure API keys in Streamlit Cloud Secrets to enable RAG search."
            )
            st.info("Required secrets: QDRANT_URL, OPENROUTER_API_KEY")
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Please configure API keys to enable RAG search.",
            }
        )

st.divider()
st.caption("Powered by Qdrant + OpenRouter")
