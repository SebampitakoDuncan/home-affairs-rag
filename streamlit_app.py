import os
import streamlit as st

st.set_page_config(
    page_title="Home Affairs RAG",
    page_icon="🏠",
    layout="wide",
)

# Add Google Fonts DM Sans using CSS @import
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    .stApp, .stMarkdown, .stTextInput, .stChatInput, .stChatMessage {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    * {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 Home Affairs RAG System")
st.markdown("Ask questions about Australian visas, citizenship, and immigration.")

# Check if environment variables are set
qdrant_url = os.getenv("QDRANT_URL")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_key:
    st.warning("⚠️ OPENROUTER_API_KEY not set. Please set it in Secrets or add to .env")
    st.info("For local development, create a `.env` file with your API keys.")

with st.sidebar:
    st.header("⚙️ Settings")
    st.subheader("Configuration")
    qdrant_url_input = st.text_input("Qdrant URL", value=qdrant_url or "http://localhost:6333")
    qdrant_url = qdrant_url_input

    api_key_input = st.text_input("OpenRouter API Key", type="password", value=openrouter_key)
    if api_key_input:
        openrouter_key = api_key_input

    openrouter_model = st.text_input("OpenRouter Model", value=os.getenv("OPENROUTER_MODEL", "gpt-4o-mini"))

    st.divider()
    st.markdown("**Streamlit Cloud Deployment Instructions:**")
    st.markdown("""
    1. Fork/copy this repository
    2. Connect to Streamlit Cloud
    3. Add these Secrets:
       - `QDRANT_URL` (or use Qdrant Cloud)
       - `OPENROUTER_API_KEY` (your OpenRouter key)
       - `OPENROUTER_MODEL` (optional, defaults to gpt-4o-mini)
    4. Deploy!
    """)

    st.divider()
    st.subheader("Docker Version")
    st.markdown("The Docker version includes Qdrant and handles environment automatically. Use `docker-compose up`.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your question about Australian visas..."):
    if not openrouter_key:
        st.error("❌ Please set OPENROUTER_API_KEY in settings or Secrets")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    import httpx

                    # Search Qdrant
                    qdrant_response = httpx.post(
                        f"{qdrant_url}/collections/home_affairs_docs/points/query",
                        json={
                            "vector": [0.1] * 384,
                            "limit": 3,
                        },
                        timeout=30.0,
                    )

                    if qdrant_response.status_code == 200:
                        results = qdrant_response.json().get("result", [])

                        if not results:
                            st.info("No relevant documents found in the knowledge base.")
                        else:
                            context_parts = []
                            sources = []

                            for idx, point in enumerate(results):
                                payload = point.get("payload", {})
                                text = payload.get("text", "")
                                title = payload.get("title", "Unknown")
                                url = payload.get("url", "")
                                context_parts.append(f"Document {idx + 1}:\\n{text}")
                                sources.append(f"[{idx + 1}] {title}\\n{url}")

                            context = "\\n\\n".join(context_parts)

                            # Generate response with OpenRouter
                            rag_prompt = "Use the following documents to answer the question.\\n\\nDocuments:\\n" + context + "\\n\\nQuestion: " + prompt + "\\n\\nProvide a clear, informative answer based on the documents. Include source URLs at the end."

                            openrouter_response = httpx.post(
                                "https://openrouter.ai/api/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {openrouter_key}",
                                    "HTTP-Referer": "https://openrouter.ai",
                                    "Content-Type": "application/json",
                                },
                                json={
                                    "model": openrouter_model,
                                    "messages": [{"role": "user", "content": rag_prompt}],
                                    "temperature": 0,
                                },
                                timeout=30.0,
                            )

                            if openrouter_response.status_code == 200:
                                answer = openrouter_response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from OpenRouter")

                                st.markdown(answer)

                                st.markdown("---")
                                st.markdown("**Sources:**")
                                for source in sources:
                                    st.markdown(source)

                                st.session_state.messages.append({"role": "assistant", "content": answer})

                            else:
                                st.error(f"OpenRouter API error: {openrouter_response.status_code}")

                    else:
                        st.error(f"Qdrant error: {qdrant_response.status_code}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.divider()
st.caption("Powered by Qdrant + OpenRouter")
