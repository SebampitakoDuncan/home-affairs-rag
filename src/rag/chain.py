"""
RAG Chain - RAG pipeline with OpenRouter
"""

import os
import sys
import logging
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Add src to path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_rag_chain(retriever, llm=None):
    """Create RAG chain with OpenRouter"""
    try:
        openrouter_base_url = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        openrouter_model = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")

        if llm is None:
            llm = OpenAI(
                base_url=openrouter_base_url,
                api_key=openrouter_key,
            )

        logger.info(f"OpenAI initialized (model: {openrouter_model})")

        from rag.prompts import RAG_PROMPT
        from rag.retriever import format_docs_with_metadata, format_sources_for_response

        def rag_chain(question):
            # Retrieve relevant documents
            docs = retriever.invoke(question)

            if not docs:
                return {
                    "answer": "I couldn't find relevant information in the documents to answer your question.",
                    "sources": "No sources available.",
                    "docs": [],
                }

            # Format context and sources
            context = format_docs_with_metadata(docs)
            sources = format_sources_for_response(docs)

            # Create prompt
            prompt = RAG_PROMPT.format(
                context=context,
                question=question,
            )

            # Generate response
            response = llm.chat.completions.create(
                model=openrouter_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )

            answer = response.choices[0].message.content

            logger.info(f"Generated response (length: {len(answer)})")

            return {
                "answer": answer,
                "sources": sources,
                "docs": docs,
            }

        return rag_chain

    except Exception as e:
        logger.error(f"Error creating RAG chain: {e}")
        raise


# Create global instance by default
def create_default_rag_chain():
    """Create default RAG chain"""
    from rag.retriever import create_retriever

    retriever = create_retriever()
    return create_rag_chain(retriever=retriever)
