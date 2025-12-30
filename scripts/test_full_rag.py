#!/usr/bin/env python
"""
Full RAG Test - Test complete pipeline with real APIs (Direct Qdrant)
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vectorstore.qdrant_store import qdrant_store
from embeddings.fastembed import fastembed
from processors.text_cleaner import text_cleaner
from processors.chunker import chunker
from rag.prompts import RAG_PROMPT
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def test_full_rag():
    """Test full RAG pipeline with real APIs"""

    print("=" * 70)
    print("Full RAG Pipeline Test (Direct Qdrant + OpenRouter)")
    print("=" * 70)

    # 1. Create collection
    print("\n1. Creating test collection...")
    collection_name = "test_full_rag"
    if qdrant_store.create_collection(collection_name, recreate=True):
        print(f"✅ Collection created")
    else:
        print("❌ Failed to create collection")
        return False

    # 2. Add test documents
    print("\n2. Adding test documents...")
    test_docs = [
        {
            "text": """
            Subclass 189 Visa - Skilled Independent Visa
            The Subclass 189 visa is a permanent residence visa for skilled workers who are not sponsored.

            Key Requirements:
            - Age: Must be under 45 years
            - English: Competent English (IELTS 6.0 or equivalent)
            - Skills: Skills assessment for nominated occupation
            - Points: Minimum 65 points on points test

            Visa Cost: AUD 4,770
            Processing Time: 8-11 months
            """,
            "source": "https://homeaffairs.gov.au/visa/189",
            "title": "Subclass 189 Visa",
        },
        {
            "text": """
            Subclass 190 Visa - Skilled Nominated Visa
            The Subclass 190 visa is for skilled workers nominated by an Australian state or territory.

            Key Requirements:
            - Age: Must be under 45 years
            - English: Competent English (IELTS 6.0 or equivalent)
            - Skills: Skills assessment for nominated occupation
            - Points: Minimum 65 points on points test
            - State Nomination: Must have state nomination

            Visa Cost: AUD 4,770
            Processing Time: 7-10 months
            """,
            "source": "https://homeaffairs.gov.au/visa/190",
            "title": "Subclass 190 Visa",
        },
    ]

    vectors = []
    payloads = []
    ids = []

    for doc_id, doc in enumerate(test_docs):
        clean_text = text_cleaner.normalize_whitespace(doc["text"])
        chunked_docs = chunker.chunk_document(clean_text)

        for chunk in chunked_docs:
            vectors.append(fastembed.embed_query(chunk.page_content))
            payloads.append(
                {
                    "text": chunk.page_content,
                    "url": doc["source"],
                    "title": doc["title"],
                }
            )
            ids.append(doc_id)

    print(f"   Added {len(vectors)} vectors")

    if qdrant_store.upsert_vectors(
        vectors, payloads, ids, collection_name=collection_name
    ):
        print("✅ Documents added to Qdrant")
    else:
        print("❌ Failed to add documents")
        return False

    # 3. Test RAG query
    print("\n3. Testing RAG query with OpenRouter...")

    try:
        # Search for relevant documents
        test_query = "What are the requirements for a 189 visa?"
        print(f"   Query: {test_query}")

        query_embedding = fastembed.embed_query(test_query)

        results = qdrant_store.search(
            query_vector=query_embedding,
            limit=3,
            score_threshold=0.3,
            collection_name=collection_name,
        )

        print(f"   Found {len(results)} relevant documents")

        # Format context
        context_parts = []
        sources = []

        for idx, result in enumerate(results):
            payload = result.payload
            context_parts.append(f"Document {idx + 1}:\n{payload.get('text', '')}")
            sources.append(
                f"[{idx + 1}] {payload.get('title', 'Unknown')}\n{payload.get('url', '')}"
            )

        context = "\n\n".join(context_parts)

        # Generate response with OpenRouter
        print("\n   Generating response with OpenRouter...")

        prompt = RAG_PROMPT.format(
            context=context,
            question=test_query,
        )

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

        # Display results
        print("\n" + "=" * 70)
        print("Response:")
        print("=" * 70)
        print(answer)

        print("\n" + "=" * 70)
        print("Sources:")
        print("=" * 70)
        print("\n".join(sources))

        # Cleanup
        print("\n4. Cleanup...")
        qdrant_store.delete_collection(collection_name)
        print("✅ Test collection deleted")

        print("\n" + "=" * 70)
        print("Full RAG pipeline test successful! 🎉")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_rag()
    sys.exit(0 if success else 1)
