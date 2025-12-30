"""
Chunker - Split documents into chunks for embedding
"""

import os
import logging
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunk documents for embedding"""

    def __init__(self):
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))

        # Initialize LangChain splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        logger.info(
            f"Chunker initialized (size: {self.chunk_size}, overlap: {self.chunk_overlap})"
        )

    def chunk_document(self, text: str, metadata: Optional[dict] = None) -> List[dict]:
        """Chunk a single document"""
        try:
            chunks = self.splitter.create_documents([text])

            # Add metadata to each chunk
            result = []
            total_chunks = len(chunks)

            for idx, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update(
                    {
                        "chunk_id": idx,
                        "total_chunks": total_chunks,
                    }
                )
                chunk.metadata = chunk_metadata
                result.append(chunk)

            logger.info(f"Chunked document into {total_chunks} chunks")
            return result

        except Exception as e:
            logger.error(f"Error chunking document: {e}")
            raise

    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """Chunk multiple documents"""
        try:
            all_chunks = []

            for doc in documents:
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Chunk this document
                chunks = self.chunk_document(text, metadata)
                all_chunks.extend(chunks)

            logger.info(
                f"Chunked {len(documents)} documents into {len(all_chunks)} chunks"
            )
            return all_chunks

        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise


# Global instance
chunker = DocumentChunker()
