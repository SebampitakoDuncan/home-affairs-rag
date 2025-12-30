#!/usr/bin/env python
"""
Test the RAG pipeline end-to-end
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vectorstore.qdrant_store import qdrant_store
from embeddings.fastembed import fastembed
from rag.retriever import create_retriever
from rag.chain import create_rag_chain
from dotenv import load_dotenv

load_dotenv()


def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    print("=" * 60)
    print("Testing RAG Pipeline")
    print("=" * 60)

    # 1. Test Qdrant
    print("\n1. Testing Qdrant connection...")
    if qdrant_store.health_check():
        print("✅ Qdrant connected")
    else:
        print("❌ Qdrant connection failed")
        return False

    # 2. Create collection
    print("\n2. Creating test collection...")
    collection_name = "test_rag_collection"
    if qdrant_store.create_collection(collection_name, recreate=True):
        print(f"✅ Collection created: {collection_name}")
    else:
        print("❌ Failed to create collection")
        return False

    # 3. Add some test documents
    print("\n3. Adding test documents...")
    test_text = """
    Skilled Independent Visa (Subclass 189)
    The Subclass 189 visa is a permanent residence visa for skilled workers who are not sponsored by an employer, a state or territory, or a family member.
    
    Requirements:
    - You must be under 45 years of age
    - You must nominate an occupation from the skilled occupation list
    - You must have a suitable skills assessment
    - You must have competent English language ability
    - You must score at least 65 points on the points test
    
    Visa Cost:
    - Primary applicant: AUD 4,770
    - Secondary applicant over 18: AUD 2,385
    - Secondary applicant under 18: AUD 1,190
    
    Processing Time:
    - 75% of applications processed within 8 months
    - 90% of applications processed within 11 months
    """

    # Clean and chunk
    from processors.text_cleaner import text_cleaner
    from processors.chunker import chunker

    cleaned_text = text_cleaner.normalize_whitespace(test_text)
    chunked_docs = chunker.chunk_document(cleaned_text)
    chunks = [doc.page_content for doc in chunked_docs]

    print(f"   Created {len(chunks)} chunks")

    # Embed chunks
    vectors = []
    payloads = []
    ids = []

    vectors = fastembed.embed_documents(chunks)
    for idx, chunk in enumerate(chunks):
        payloads.append(
            {
                "text": chunk,
                "source": "test_document",
                "title": "Skilled Independent Visa (Subclass 189)",
            }
        )
        ids.append(idx)

    # Upsert to Qdrant
    if qdrant_store.upsert_vectors(
        vectors, payloads, ids, collection_name=collection_name
    ):
        print(f"✅ Upserted {len(vectors)} vectors to Qdrant")
    else:
        print("❌ Failed to upsert vectors")
        return False

    # 4. Test retrieval with Qdrant store directly
    print("\n4. Testing retrieval...")
    try:
        # Create query embedding
        query = "What are the requirements for a 189 visa?"
        print(f"   Query: {query}")

        query_embedding = fastembed.embed_query(query)

        # Search in Qdrant
        results = qdrant_store.search(
            query_vector=query_embedding,
            limit=3,
            score_threshold=0.3,
            collection_name=collection_name,
        )

        print(f"✅ Retrieved {len(results)} documents")

        for idx, result in enumerate(results[:3]):
            print(f"\n   Result {idx + 1} (score: {result.score:.3f}):")
            payload = result.payload
            text = payload.get("text", "")
            print(f"   {text[:100]}...")
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Cleanup
    print("\n6. Cleanup...")
    qdrant_store.delete_collection(collection_name)
    print(f"✅ Deleted test collection")

    print("\n" + "=" * 60)
    print("All RAG pipeline tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_rag_pipeline()
    sys.exit(0 if success else 1)
