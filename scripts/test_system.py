"""
Test System - End-to-end system testing
"""

import os
import sys
import logging

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_qdrant_connection():
    """Test Qdrant connection"""
    try:
        from vectorstore.qdrant_store import qdrant_store

        logger.info("Testing Qdrant connection...")
        if qdrant_store.health_check():
            logger.info("Qdrant connection successful")
            return True
        else:
            logger.error("Qdrant connection failed")
            return False
    except Exception as e:
        logger.error(f"Qdrant test error: {e}")
        return False


def test_collection_creation():
    """Test creating Qdrant collection"""
    try:
        from vectorstore.qdrant_store import qdrant_store

        logger.info("Testing collection creation...")
        if qdrant_store.create_collection("test_collection", recreate=True):
            logger.info("Collection creation successful")

            # Get collection info
            info = qdrant_store.get_collection_info("test_collection")
            logger.info(f"Collection info: {info}")

            return True
        else:
            logger.error("Collection creation failed")
            return False
    except Exception as e:
        logger.error(f"Collection test error: {e}")
        return False


def test_fastembed():
    """Test FastEmbed embeddings"""
    try:
        from embeddings.fastembed import fastembed

        logger.info("Testing FastEmbed embeddings...")

        # Test embedding a query
        test_text = "What are requirements for a 189 visa?"
        embedding = fastembed.embed_query(test_text)

        logger.info(f"FastEmbed working (embedding size: {len(embedding)})")
        logger.info(f"Test query embedded: {test_text[:50]}...")

        return True
    except Exception as e:
        logger.error(f"FastEmbed test error: {e}")
        return False


def test_document_processing():
    """Test document processing"""
    try:
        from processors.text_cleaner import text_cleaner
        from processors.chunker import chunker
        from processors.metadata import metadata_extractor

        logger.info("Testing document processing...")

        # Test HTML cleaning
        test_html = "<html><body><nav>Navigation</nav><main><h1>Test</h1><p>This is a test document.</p></main></body></html>"
        cleaned = text_cleaner.clean_html(test_html)
        logger.info("HTML cleaning working")

        # Test chunking
        chunks = chunker.chunk_document(cleaned)
        logger.info(f"Chunking working (created {len(chunks)} chunks)")

        # Test metadata extraction
        metadata = metadata_extractor.extract_all_metadata(
            test_html, "https://example.com/test"
        )
        logger.info("Metadata extraction working")

        return True
    except Exception as e:
        logger.error(f"Document processing test error: {e}")
        return False


def test_prompts():
    """Test RAG prompts"""
    try:
        from rag.prompts import SYSTEM_PROMPT, RAG_PROMPT

        logger.info("Testing RAG prompts...")

        # Verify prompts are loaded
        if SYSTEM_PROMPT and RAG_PROMPT:
            logger.info("Prompts loaded successfully")
            logger.info(f"System prompt length: {len(SYSTEM_PROMPT)} chars")
            logger.info(f"RAG prompt length: {len(RAG_PROMPT)} chars")
            return True
        else:
            logger.error("Prompts not loaded")
            return False
    except Exception as e:
        logger.error(f"Prompts test error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Starting Home Affairs RAG System Tests")
    logger.info("=" * 60)

    results = {}

    # Run tests
    results["qdrant_connection"] = test_qdrant_connection()
    results["collection_creation"] = test_collection_creation()
    results["fastembed"] = test_fastembed()
    results["document_processing"] = test_document_processing()
    results["prompts"] = test_prompts()

    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")

    logger.info("=" * 60)
    logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
    logger.info(f"Tests Failed: {total_tests - passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        logger.info("All tests passed! System is ready.")
        return 0
    else:
        logger.warning("Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
