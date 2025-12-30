"""
Retriever - LangChain retriever from Qdrant
"""

import os
import sys
import logging
from typing import List, Optional
from langchain_qdrant import Qdrant
from langchain_core.documents import Document
from dotenv import load_dotenv

# Add src to path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_retriever(
    top_k: int = 5, score_threshold: float = 0.5, collection_name: str = None
):
    """Create LangChain retriever from Qdrant"""
    try:
        from vectorstore.qdrant_store import qdrant_store
        from embeddings.fastembed import fastembed

        if collection_name is None:
            collection_name = os.getenv("QDRANT_COLLECTION_NAME", "home_affairs_docs")

        logger.info(f"Creating retriever for collection: {collection_name}")
        logger.info(f"Top-k: {top_k}, Threshold: {score_threshold}")

        # Create document retriever from Qdrant with embeddings
        retriever = Qdrant(
            client=qdrant_store.client,
            collection_name=collection_name,
            embedding=fastembed.model,
        )

        logger.info("Retriever created successfully")
        return retriever

    except Exception as e:
        logger.error(f"Error creating retriever: {e}")
        raise


def format_docs_with_metadata(docs: List[Document]) -> str:
    """Format documents with source information for citations"""
    if not docs:
        return "No documents found."

    formatted = []
    for idx, doc in enumerate(docs):
        metadata = doc.metadata
        url = metadata.get("url", "")
        title = metadata.get("title", "")

        formatted.append(f"Source {idx + 1} ({title})\nURL: {url}")
        formatted.append(doc.page_content)

    return "\n\n".join(formatted)


def format_sources_for_response(docs: List[Document]) -> str:
    """Format sources for final response"""
    sources = []
    for idx, doc in enumerate(docs):
        metadata = doc.metadata
        url = metadata.get("url", "")
        title = metadata.get("title", "")
        sources.append(f"[{idx + 1}] {title}\n{url}")

    if not sources:
        return "No sources available."

    return "\n".join(sources)
