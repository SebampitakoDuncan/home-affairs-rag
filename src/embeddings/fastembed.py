"""
FastEmbed - Local vector embeddings for documents
"""

import os
import logging
from typing import List
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FastEmbedWrapper:
    """FastEmbed wrapper for local vector generation"""

    def __init__(self):
        """Initialize FastEmbed model"""
        self.model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self.device = os.getenv("EMBEDDING_DEVICE", "cpu")

        logger.info(f"Loading FastEmbed model: {self.model_name} on {self.device}")

        self.model = TextEmbedding(
            model_name=self.model_name,
            device=self.device,
        )

        test_embedding = next(self.model.embed(["test"]))
        self.embedding_size = len(test_embedding)

        logger.info(f"FastEmbed model loaded (size: {self.embedding_size})")

    def embed_documents(
        self, texts: List[str], batch_size: int = 32, show_progress: bool = True
    ) -> List[List[float]]:
        all_embeddings = []
        total_texts = len(texts)

        for i in range(0, total_texts, batch_size):
            batch_end = min(i + batch_size, total_texts)
            batch_texts = texts[i:batch_end]

            batch_embeddings = list(self.model.embed(batch_texts))
            all_embeddings.extend(batch_embeddings)

            if show_progress:
                logger.info(f"Embedded {batch_end}/{total_texts} documents")

        logger.info(f"Embedded {total_texts} documents")
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        embedding = list(self.model.embed([text]))[0]
        logger.debug(f"Embedded query (length: {len(embedding)})")
        return embedding

    def get_embedding_size(self) -> int:
        return self.embedding_size


fastembed = FastEmbedWrapper()
