#!/usr/bin/env python
"""
Update Database Script - Check crawl status and process results
"""

import os
import sys
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from crawler.firecrawl_client import firecrawl_client
from vectorstore.qdrant_store import qdrant_store
from embeddings.fastembed import fastembed
from processors.text_cleaner import text_cleaner
from processors.chunker import chunker
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_crawl_results(data):
    """Process crawled documents and embed into Qdrant"""

    print("\nProcessing crawled documents...")
    print("=" * 60)

    # Extract text and metadata from crawled data
    documents = []
    for item in data:
        markdown = item.get("markdown", "")
        metadata = item.get("metadata", {})

        if markdown and len(markdown) > 100:  # Skip very short documents
            documents.append(
                {
                    "text": markdown,
                    "url": metadata.get("sourceURL", ""),
                    "title": metadata.get("title", "Untitled"),
                }
            )

    print(f"✅ Found {len(documents)} valid documents")

    if len(documents) == 0:
        print("❌ No documents to process")
        return False

    # Process documents
    vectors = []
    payloads = []
    ids = []
    doc_id = 0

    for doc in documents:
        # Clean text
        clean_text = text_cleaner.normalize_whitespace(doc["text"])

        # Chunk document
        chunks = chunker.chunk_document(
            clean_text, metadata={"source": doc["url"], "title": doc["title"]}
        )

        # Embed chunks
        chunk_texts = [c.page_content for c in chunks]
        embeddings = fastembed.embed_documents(chunk_texts)

        # Add to batch
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append(embedding)
            payloads.append(
                {
                    "text": chunk.page_content,
                    "url": doc["url"],
                    "title": doc["title"],
                    "chunk_index": chunk.metadata.get("chunk_index", 0),
                }
            )
            ids.append(doc_id)
            doc_id += 1

        print(f"   Processed document: {doc['title'][:50]}... ({len(chunks)} chunks)")

    # Upsert to Qdrant
    print(f"\nUpserting {len(vectors)} vectors to Qdrant...")
    if qdrant_store.upsert_vectors(vectors, payloads, ids):
        print("✅ Successfully added documents to knowledge base")
        return True
    else:
        print("❌ Failed to add documents to knowledge base")
        return False


def check_crawl_status(job_id):
    """Check status of a crawl job"""

    print(f"Checking status for job: {job_id}")
    print("=" * 60)

    status = firecrawl_client.get_crawl_status(job_id)

    if not status.get("success"):
        print(f"❌ Failed to get status: {status.get('error', 'Unknown error')}")
        return None

    crawl_status = status.get("status")
    total = status.get("total", 0)
    progress = status.get("progress", 0)

    print(f"Status: {crawl_status}")
    print(f"Total documents: {total}")
    print(f"Progress: {progress}/{total}")

    if crawl_status == "completed":
        data = status.get("data", [])
        print(f"✅ Crawl completed with {len(data)} documents")

        # Process results
        if data:
            process_crawl_results(data)

    elif crawl_status == "failed":
        print("❌ Crawl failed")

    else:
        print(f"⏳ Crawl in progress...")

    return status


def main():
    """Main function to update database"""

    print("=" * 60)
    print("Update Database - Crawl Status and Processing")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("\n❌ Error: FIRECRAWL_API_KEY not found in .env file")
        return 1

    # Ask for job ID
    job_id = input("\nEnter crawl job ID (or press Enter to skip): ").strip()

    if job_id:
        # Check status of specific job
        check_crawl_status(job_id)
    else:
        print("\nNo job ID provided. Exiting.")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
