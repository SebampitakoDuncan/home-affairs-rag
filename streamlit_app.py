import streamlit as st
import os
import json

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

# Get API keys from environment or sidebar
qdrant_url = os.getenv("QDRANT_URL", "")
qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
openrouter_model = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")

with st.sidebar:
    st.header("⚙️ Settings")
    qdrant_url_input = st.text_input(
        "Qdrant URL",
        value=qdrant_url
        or "https://22c03635-e552-40f6-9170-2ff1ff9b0153.europe-west3-0.gcp.cloud.qdrant.io:6333",
    )
    qdrant_url = qdrant_url_input

    qdrant_api_key_input = st.text_input(
        "Qdrant API Key", type="password", value=qdrant_api_key
    )
    if qdrant_api_key_input:
        qdrant_api_key = qdrant_api_key_input

    openrouter_key_input = st.text_input(
        "OpenRouter API Key", type="password", value=openrouter_key
    )
    if openrouter_key_input:
        openrouter_key = openrouter_key_input

    openrouter_model_input = st.text_input(
        "Model", value=openrouter_model or "gpt-4o-mini"
    )
    if openrouter_model_input:
        openrouter_model = openrouter_model_input

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your question about Australian visas..."):
    if not openrouter_key:
        st.error("❌ Please set OPENROUTER_API_KEY in Settings")
    elif not qdrant_url or not qdrant_api_key:
        st.error("❌ Please set QDRANT_URL and QDRANT_API_KEY in Settings")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                try:
                    import httpx

                    # Search Qdrant Cloud
                    search_response = httpx.post(
                        f"{qdrant_url}/collections/home_affairs_docs/points/query",
                        headers={"Authorization": f"Bearer {qdrant_api_key}"},
                        json={"query": [0.1] * 384, "limit": 3},
                        timeout=30.0,
                    )

                    if search_response.status_code == 200:
                        results = (
                            search_response.json().get("result", {}).get("points", [])
                        )

                        if not results:
                            st.info("No documents found in knowledge base.")
                        else:
                            context_parts = []
                            sources = []

                            for idx, point in enumerate(results):
                                payload = point.get("payload", {})
                                text = payload.get("text", "")
                                title = payload.get("title", "Unknown")
                                url = payload.get("url", "")
                                context_parts.append(f"[{idx + 1}] {title}\n{text}")
                                sources.append(f"[{idx + 1}] {title}\n{url}")

                            context = "\n\n".join(context_parts)

                            # Get answer from OpenRouter
                            rag_prompt = f"""Use these documents to answer the question.

Documents:
{context}

Question: {prompt}

Answer:"""

                            llm_response = httpx.post(
                                "https://openrouter.ai/api/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {openrouter_key}",
                                    "Content-Type": "application/json",
                                },
                                json={
                                    "model": openrouter_model,
                                    "messages": [
                                        {"role": "user", "content": rag_prompt}
                                    ],
                                },
                                timeout=30.0,
                            )

                            if llm_response.status_code == 200:
                                answer = llm_response.json()["choices"][0]["message"][
                                    "content"
                                ]
                                st.markdown(answer)

                                st.markdown("---")
                                st.markdown("**Sources:**")
                                for source in sources:
                                    st.markdown(source)

                                st.session_state.messages.append(
                                    {"role": "assistant", "content": answer}
                                )
                            else:
                                st.error(
                                    f"OpenRouter error: {llm_response.status_code}"
                                )
                    else:
                        st.error(f"Qdrant error: {search_response.status_code}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.divider()
st.caption("Powered by Qdrant Cloud + OpenRouter")
