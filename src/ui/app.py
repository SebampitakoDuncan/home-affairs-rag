"""
Home Affairs RAG System - Main Streamlit Application
Linear/AI SDK Inspired Professional UI
"""

import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from vectorstore.qdrant_store import qdrant_store
from embeddings.fastembed import fastembed
from ui.components import (
    render_chat_message,
    render_citations,
    render_upload_zone,
)
from ui.constants import (
    THEME_COLORS,
    UI_CONFIG,
    CHAT_CONFIG,
    STATUS_MESSAGES,
    FOOTER_CREDITS,
)

WELCOME_MESSAGE = CHAT_CONFIG["welcome_message"]
TYPING_INDICATOR = CHAT_CONFIG["typing_indicator"]
ERROR_MESSAGE = "An error occurred. Please try again."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main Streamlit application"""

    # Page config
    st.set_page_config(
        page_title=os.getenv("STREAMLIT_TITLE", "Home Affairs RAG System"),
        page_icon=os.getenv("STREAMLIT_PAGE_ICON", "🏠"),
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown(f"""
        <style>
            .stApp {{
                color: {THEME_COLORS["text"]};
                background-color: {THEME_COLORS["background"]};
            }}
            .stButton > button {{
                border-radius: 0.375rem;
                transition: all 0.2s ease;
            }}
            .stTextInput > div > div > input {{
                background-color: #1F2937;
                border-color: #374151;
                color: {THEME_COLORS["text"]};
                border-radius: 0.375rem;
            }}
        </style>
    """)

    # Header
    with st.container():
        col1, col2, col3 = st.columns([1, 10, 1])

        with col1:
            st.markdown("# 🏠 Home Affairs RAG System")

        with col2:
            if st.button("⚙️ Settings", key="settings", help="System settings"):
                st.session_state.settings_open = not st.session_state.get(
                    "settings_open", False
                )
                with st.expander("Settings", expanded=True):
                    st.subheader("Settings")
                    st.text_input(
                        "API Keys Configuration",
                        value=os.getenv("OPENROUTER_MODEL", ""),
                        disabled=True,
                    )
                    st.text_input(
                        "Crawl Limit", value=os.getenv("CRAWL_LIMIT", ""), disabled=True
                    )
                    st.text_input(
                        "Chunk Size", value=os.getenv("CHUNK_SIZE", ""), disabled=True
                    )
                    st.text_input(
                        "Top K Results",
                        value=os.getenv("TOP_K_RESULTS", ""),
                        disabled=True,
                    )

    st.markdown("---")

    # Welcome message
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display welcome message for new sessions
    if not st.session_state.get("welcome_shown"):
        st.info("Welcome! Showing welcome message")
        render_chat_message(WELCOME_MESSAGE, "assistant")
        st.session_state.welcome_shown = True

    # File upload section
    with st.container(border=True):
        st.subheader("📤 Upload Documents")
        render_upload_zone()

        # Chat history
        st.subheader("💬 Chat History (Last 50 messages)")

        # Display chat messages
        messages = st.session_state.get("messages", [])
        for idx, message in enumerate(messages[-UI_CONFIG["max_chat_history"] :]):
            render_chat_message(message.get("content"), message.get("role"))

        # Input field
        user_input = st.chat_input(
            "Ask your question about Home Affairs...", key="chat_input"
        )

        # Send button
        col_send, col_clear = st.columns([4, 1])

        with col_send:
            send_button = st.button("Send", use_container_width=True)
            if send_button and user_input:
                with st.spinner("Thinking..."):
                    process_query(user_input)

        with col_clear:
            if st.button("📎 Clear Chat"):
                st.session_state.messages = []
                st.rerun()

    # Footer
    st.markdown("---")
    st.caption(
        f"Powered by: {FOOTER_CREDITS['vector_db']} + {FOOTER_CREDITS['embeddings']} + {FOOTER_CREDITS['llm']}"
    )


def process_query(question: str):
    """Process user query and return answer"""
    try:
        if not question or not question.strip():
            st.warning("Please enter a question.")
            return

        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": question})

        # Search for relevant documents
        query_embedding = fastembed.embed_query(question)

        results = qdrant_store.search(
            query_vector=query_embedding,
            limit=3,
            score_threshold=0.3,
        )

        if not results:
            st.info(
                "I couldn't find relevant information in the knowledge base. "
                "Try uploading documents or rephrasing your question."
            )
            return

        # Format context
        context_parts = []
        sources = []

        for idx, result in enumerate(results):
            payload = result.payload
            context_parts.append(f"Document {idx + 1}:\n{payload.get('text', '')}")
            sources.append(
                {
                    "title": payload.get("title", "Unknown"),
                    "url": payload.get("url", ""),
                    "confidence": result.score,
                }
            )

        context = "\n\n".join(context_parts)

        # Generate response with OpenRouter
        from rag.prompts import RAG_PROMPT

        prompt = RAG_PROMPT.format(
            context=context,
            question=question,
        )

        from openai import OpenAI

        client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        answer = response.choices[0].message.content

        # Add assistant message to history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

        # Display answer
        render_chat_message(answer, "assistant")

        # Display citations
        if sources:
            st.markdown("### 📄 Sources")
            source_urls = [s["url"] for s in sources]
            render_citations(sources, source_urls)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        import traceback

        traceback.print_exc()
        st.error(ERROR_MESSAGE)
        render_chat_message(f"Error: {e}", "assistant")


if __name__ == "__main__":
    main()
