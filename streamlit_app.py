"""
Home Affairs RAG System - Streamlit Cloud Version
This version is ready for deployment to Streamlit Cloud
"""

import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Home Affairs RAG",
    page_icon="🏠",
    layout="wide",
)

# Add Google Fonts DM Sans using CSS @import
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    .stApp, .stMarkdown, .stTextInput, .stChatInput, .stChatMessage {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    * {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🏠 Home Affairs RAG System")
st.markdown("Ask questions about Australian visas, citizenship, and immigration.")

# Check if environment variables are set
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_key:
    st.warning("⚠️ OPENROUTER_API_KEY not set. Please set it in Secrets or add to .env")
    st.info("For local development, create a `.env` file with your API keys.")

with st.sidebar:
    st.header("⚙️ Settings")
    st.subheader("Configuration")

    qdrant_url_input = st.text_input("Qdrant URL", value=qdrant_url)
    qdrant_url = qdrant_url_input

    api_key_input = st.text_input(
        "OpenRouter API Key", type="password", value=openrouter_key
    )
    if api_key_input:
        openrouter_key = api_key_input

    openrouter_model = st.text_input(
        "OpenRouter Model", value=os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
    )

    st.divider()
    st.markdown("**Streamlit Cloud Deployment Instructions:**")
    st.markdown("""
    1. Fork/copy this repository
    2. Connect to Streamlit Cloud
    3. Add these Secrets:
       - `QDRANT_URL` (or use Qdrant Cloud)
       - `OPENROUTER_API_KEY` (your OpenRouter key)
    4. Add `OPENROUTER_MODEL` (optional, defaults to gpt-4o-mini)
    """)

    st.divider()
    st.subheader("Docker Version")
    st.markdown(
        "The Docker version includes Qdrant and handles environment automatically. Use `docker-compose up`."
    )

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
                    from vectorstore.qdrant_store import qdrant_store
                    from embeddings.fastembed import fastembed
                    from openai import OpenAI

                    query_embedding = fastembed.embed_query(prompt)

                    results = qdrant_store.search(
                        query_vector=query_embedding,
                        limit=3,
                        score_threshold=0.3,
                    )

                    if not results:
                        st.info(
                            "No relevant documents found in the knowledge base. Try asking a different question or uploading documents."
                        )
                    else:
                        context_parts = []
                        sources = []

                        for idx, result in enumerate(results):
                            payload = result.payload
                            text = payload.get("text", "")
                            title = payload.get("title", "Unknown")
                            url = payload.get("url", "")
                            context_parts.append(f"Document {idx + 1}:\n{text}")
                            sources.append(f"[{idx + 1}] {title}\n{url}")

                        context = "\n\n".join(context_parts)

                        rag_prompt = f"""Use the following documents to answer the question.\n\nDocuments:\n{context}\n\nQuestion: {prompt}\n\nProvide a clear, informative answer based on the documents. Include the source URLs at the end."""

                        client = OpenAI(
                            base_url=os.getenv(
                                "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
                            ),
                            api_key=openrouter_key,
                        )

                        response = client.chat.completions.create(
                            model=openrouter_model,
                            messages=[{"role": "user", "content": rag_prompt}],
                            temperature=0,
                        )

                        answer = response.choices[0].message.content
                        st.markdown(answer)

                        st.markdown("---")
                        st.markdown("**Sources:**")
                        for source in sources:
                            st.markdown(source)

                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Error: {e}", exc_info=True)

st.divider()
st.caption("Powered by Qdrant + FastEmbed + OpenRouter")
