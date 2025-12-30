"""
Qdrant Vector Store - Manages vector operations for RAG system
"""

import os
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantStore:
    """Qdrant client wrapper for vector operations"""

    def __init__(self):
        """Initialize Qdrant client"""
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "home_affairs_docs")
        self.uploads_collection_name = os.getenv(
            "QDRANT_UPLOADS_COLLECTION", "user_uploads"
        )

        # Initialize Qdrant client
        self.client = QdrantClient(
            host=self.host,
            port=self.port,
        )

        logger.info(f"Qdrant client initialized: {self.host}:{self.port}")

    def create_collection(
        self, collection_name: str, vector_size: int = 384, recreate: bool = False
    ) -> bool:
        """Create a collection with HNSW index"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)

            if collection_exists:
                if recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name=collection_name)
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    return True

            # Create collection with HNSW index
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                    hnsw_config=models.HnswConfigDiff(
                        m=16,  # HNSW connections
                        ef_construct=100,  # Indexing time vs quality
                    ),
                ),
            )

            logger.info(f"✅ Created collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating collection {collection_name}: {e}")
            return False

    def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: List[Any],
        collection_name: Optional[str] = None,
        batch_size: int = 100,
    ) -> bool:
        """Upsert vectors to collection in batches"""
        try:
            if collection_name is None:
                collection_name = self.collection_name

            total_vectors = len(vectors)
            success_count = 0

            # Process in batches
            for i in range(0, total_vectors, batch_size):
                batch_end = min(i + batch_size, total_vectors)
                batch_vectors = vectors[i:batch_end]
                batch_payloads = payloads[i:batch_end]
                batch_ids = ids[i:batch_end]

                # Upsert batch
                self.client.upsert(
                    collection_name=collection_name,
                    points=models.Batch(
                        ids=batch_ids,
                        vectors=batch_vectors,
                        payloads=batch_payloads,
                    ),
                )

                success_count = batch_end - i
                logger.info(f"Upserted {success_count}/{total_vectors} vectors")

            logger.info(f"✅ Successfully upserted {total_vectors} vectors")
            return True

        except Exception as e:
            logger.error(f"❌ Error upserting vectors: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.5,
        collection_name: Optional[str] = None,
        query_filter: Optional[Dict[str, Any]] = None,
    ) -> List[models.ScoredPoint]:
        """Search for similar vectors"""
        try:
            if collection_name is None:
                collection_name = self.collection_name

            # Build filter if provided
            search_filter = None
            if query_filter:
                # Convert dict to Qdrant filter
                filter_conditions = []
                for key, value in query_filter.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value),
                        )
                    )
                search_filter = models.Filter(must=filter_conditions)

            # Search using query_points
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                query_filter=search_filter,
                score_threshold=score_threshold,
            ).points

            return results

        except Exception as e:
            logger.error(f"❌ Error searching vectors: {e}")
            return []

    def get_collection_info(
        self, collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get collection information"""
        try:
            if collection_name is None:
                collection_name = self.collection_name

            info = self.client.get_collection(collection_name=collection_name)
            vector_size = 384  # Default for bge-small-en-v1.5
            return {
                "name": collection_name,
                "vector_size": vector_size,
                "points_count": info.points_count,
                "status": str(info.status),
            }

        except Exception as e:
            logger.error(f"❌ Error getting collection info: {e}")
            return {}

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting collection {collection_name}: {e}")
            return False

    def health_check(self) -> bool:
        """Check if Qdrant is running"""
        try:
            collections = self.client.get_collections()
            logger.info(
                f"✅ Qdrant is running ({len(collections.collections)} collections)"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Qdrant health check failed: {e}")
            return False

    def count_points(self, collection_name: Optional[str] = None) -> Optional[int]:
        """Count points in collection"""
        try:
            if collection_name is None:
                collection_name = self.collection_name

            info = self.client.get_collection(collection_name=collection_name)
            return info.points_count
        except Exception as e:
            logger.error(f"❌ Error counting points: {e}")
            return None


# Global instance
qdrant_store = QdrantStore()
