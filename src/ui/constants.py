"""
UI Constants - Linear/AI SDK Inspired Theme and Configuration
"""

# Theme colors - Linear/AI SDK inspired
THEME_COLORS = {
    "primary": "#5E6AD2",
    "background": "#0A0A0A",
    "secondary": "#1F2937",
    "text": "#F9FAFB",
    "success": "#10B981",
    "error": "#EF4444",
    "border": "#374151",
}

# UI configuration
UI_CONFIG = {
    "max_upload_size_mb": 200,
    "max_chat_history": 50,
    "typing_speed_ms": 10,
    "animation_duration_ms": 300,
}

# Chat configuration
CHAT_CONFIG = {
    "system_name": "Home Affairs RAG",
    "welcome_message": "Hello! I'm your AI assistant for Australian Department of Home Affairs information. Ask me anything about visas, citizenship, border security, or other Home Affairs topics.",
    "placeholder": "Ask your question about Home Affairs...",
    "typing_indicator": "AI is thinking...",
}

# RAG configuration
RAG_CONFIG = {
    "top_k": 5,
    "similarity_threshold": 0.5,
    "stream_chunk_size": 50,
}

# System status messages
STATUS_MESSAGES = {
    "qdrant_connected": "✅ Vector database connected",
    "qdrant_disconnected": "❌ Vector database disconnected",
    "crawler_running": "🔄 Crawler running...",
    "crawler_complete": "✅ Crawl complete",
    "crawler_error": "❌ Crawler error",
    "embedding_success": "✅ Documents embedded",
    "embedding_error": "❌ Embedding failed",
    "file_uploaded": "✅ File uploaded",
    "file_upload_error": "❌ File upload failed",
}

# Footer credits
FOOTER_CREDITS = {
    "vector_db": "Qdrant",
    "embeddings": "FastEmbed",
    "llm": "OpenRouter",
    "crawler": "Firecrawl",
    "ui": "Streamlit",
}
