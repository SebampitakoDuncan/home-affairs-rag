#!/usr/bin/env python
"""
Populate Qdrant with test documents - so the UI has data to query
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vectorstore.qdrant_store import qdrant_store
from embeddings.fastembed import fastembed
from processors.text_cleaner import text_cleaner
from processors.chunker import chunker
from dotenv import load_dotenv

load_dotenv()


def main():
    """Populate Qdrant with test visa information"""

    print("=" * 60)
    print("Populating Qdrant with test documents")
    print("=" * 60)

    # Create or recreate collection
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "home_affairs_docs")
    print(f"\n1. Creating collection: {collection_name}")

    if qdrant_store.create_collection(collection_name, recreate=True):
        print("   ✅ Collection created")
    else:
        print("   ❌ Failed to create collection")
        return False

    # Test documents
    test_docs = [
        {
            "text": """
            Subclass 189 Visa - Skilled Independent Visa
            The Subclass 189 visa is a permanent residence visa for skilled workers who are not sponsored by an employer, state, territory, or family member.

            Key Requirements:
            - Age: Must be under 45 years of age
            - English: Must have competent English (IELTS 6.0 or equivalent)
            - Skills: Must have a suitable skills assessment for nominated occupation
            - Points: Must score at least 65 points on the points test

            Visa Cost:
            - Primary applicant: AUD 4,770
            - Secondary applicant over 18: AUD 2,385
            - Secondary applicant under 18: AUD 1,190

            Processing Time:
            - 75% of applications processed within 8 months
            - 90% of applications processed within 11 months
            """,
            "source": "https://homeaffairs.gov.au/visa/189",
            "title": "Subclass 189 Visa - Skilled Independent",
        },
        {
            "text": """
            Subclass 190 Visa - Skilled Nominated Visa
            The Subclass 190 visa is a permanent residence visa for skilled workers nominated by an Australian state or territory government.

            Key Requirements:
            - Age: Must be under 45 years of age
            - English: Must have competent English (IELTS 6.0 or equivalent)
            - Skills: Must have a suitable skills assessment for nominated occupation
            - Points: Must score at least 65 points on the points test
            - State Nomination: Must have state or territory nomination

            Visa Cost:
            - Primary applicant: AUD 4,770
            - Secondary applicant over 18: AUD 2,385
            - Secondary applicant under 18: AUD 1,190

            Processing Time:
            - 75% of applications processed within 7 months
            - 90% of applications processed within 10 months
            """,
            "source": "https://homeaffairs.gov.au/visa/190",
            "title": "Subclass 190 Visa - Skilled Nominated",
        },
        {
            "text": """
            Australian Citizenship by Conferral
            You may be eligible to apply for Australian citizenship by conferral if you:

            General Requirements:
            - Are aged 18 years or over
            - Are a permanent resident
            - Have lived in Australia for at least 4 years
            - Are of good character
            - Have a basic knowledge of English
            - Intend to continue to live in Australia

            Residence Requirement:
            - You must have lived in Australia for at least 4 years as a permanent resident
            - Time spent overseas as a permanent resident may count towards the 4 years
            - Certain absences may not count towards the residence period

            Citizenship Cost:
            - Standard application: AUD 540
            - Concession application: AUD 360 (eligible concession holders)

            Processing Time:
            - 90% of applications processed within 12 months
            """,
            "source": "https://homeaffairs.gov.au/citizenship",
            "title": "Australian Citizenship by Conferral",
        },
        {
            "text": """
            Visitor Visa (Subclass 600)
            The Visitor visa (subclass 600) allows you to visit Australia for:
            - Tourism
            - Visiting family or friends
            - Business activities

            Requirements:
            - Have a genuine intention to visit Australia temporarily
            - Have sufficient funds to cover your stay
            - Have adequate health insurance
            - Have no substantial criminal record
            - Meet health and character requirements

            Visa Cost:
            - Tourist stream: AUD 195
            - Sponsored Family stream: AUD 195
            - Business Visitor stream: AUD 195

            Stay Duration:
            - Tourist stream: Up to 3, 6 or 12 months
            - Sponsored Family stream: Up to 12 months
            - Business Visitor stream: Up to 3 months
            """,
            "source": "https://homeaffairs.gov.au/visa/600",
            "title": "Visitor Visa (Subclass 600)",
        },
    ]

    # Process and embed documents
    print("\n2. Processing documents...")
    vectors = []
    payloads = []
    doc_ids = []

    for doc in test_docs:
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
            doc_ids.append(len(doc_ids))

        print(f"   Processed: {doc['title']} ({len(chunked_docs)} chunks)")

    print(f"\n   Total: {len(vectors)} vectors")

    # Upsert to Qdrant
    print("\n3. Upserting to Qdrant...")
    if qdrant_store.upsert_vectors(
        vectors, payloads, doc_ids, collection_name=collection_name
    ):
        print("   ✅ Successfully added documents")
    else:
        print("   ❌ Failed to add documents")
        return False

    # Verify
    count = qdrant_store.count_points(collection_name=collection_name)
    print(f"\n4. Verification")
    print(f"   Total documents in Qdrant: {count}")

    print("\n" + "=" * 60)
    print("Qdrant populated successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
