"""
UI Components - Reusable Streamlit components
"""

import os
import sys
import streamlit as st
import logging
from typing import List, Dict, Any, Optional

# Add src to path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.constants import THEME_COLORS, UI_CONFIG, CHAT_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def render_chat_message(message: str, role: str, show_avatar: bool = True):
    """Render a chat message with avatar"""
    if role == "user":
        with st.chat_message("user", avatar="👤" if show_avatar else None):
            st.markdown(message)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message)


def render_citations(
    sources: List[Dict[str, str]], source_urls: Optional[List[str]] = None
):
    """Render clickable citations with source information"""
    if not sources:
        return ""

    with st.container():
        st.markdown("### 📄 Sources")

        for idx, source in enumerate(sources):
            if source_urls:
                url = source_urls[idx] if idx < len(source_urls) else ""
            else:
                url = source.get("url", "")
            title = source.get("title", "Untitled")
            confidence = float(source.get("confidence", 0))

            confidence_color = (
                THEME_COLORS["success"]
                if confidence > 0.7
                else THEME_COLORS["error"]
                if confidence < 0.5
                else THEME_COLORS["primary"]
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Source {idx + 1}**")
                st.markdown(f"**{title}**")
                st.markdown(f"[{url}]({url})")

            with col2:
                st.markdown(f"Confidence: **{confidence:.0%}**")

            with col3:
                if st.button("View Document", key=f"view_doc_{idx}"):
                    st.session_state[f"show_doc_{idx}"] = True


def render_confidence_score(confidence: float):
    """Render confidence score badge"""
    confidence_pct = confidence * 100

    if confidence >= 0.7:
        color = THEME_COLORS["success"]
        emoji = "✨"
    elif confidence >= 0.5:
        color = THEME_COLORS["primary"]
        emoji = "👍"
    else:
        color = THEME_COLORS["error"]
        emoji = "⚠️"

    st.markdown(f"{emoji} **{confidence_pct:.0f}%** confidence")


def render_upload_zone():
    """Render drag and drop upload zone"""
    with st.container(border=True):
        st.markdown("### 📤 Upload Document")
        st.markdown("Supports **PDF**, **TXT**, and **DOCX** formats (max 200MB)")

        uploaded_file = st.file_uploader(
            label="Drag and drop files here or click to browse",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            key="file_uploader",
            help="Upload documents to add to your knowledge base",
        )

        if uploaded_file is not None:
            for file in uploaded_file:
                st.success(f"File uploaded: {file.name}")
                st.session_state["uploaded_files"] = st.session_state.get(
                    "uploaded_files", []
                )
                st.session_state["uploaded_files"].append(file)


def render_loading_animation():
    """Render loading animation"""
    with st.spinner("Loading..."):
        for _ in range(3):
            import time

            time.sleep(0.5)


def render_status_indicator(status: str, message: Optional[str] = None):
    """Render system status indicator"""
    icon = "🟢" if status == "ready" else "🔴" if status == "running" else "⚠️"

    if message:
        st.markdown(f"**{icon}** {message}")
    else:
        st.markdown(f"**{icon}** System {status}")
