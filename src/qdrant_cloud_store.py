"""
Qdrant Cloud Client Wrapper
"""

import os
import logging
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantCloudStore:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        if api_key and qdrant_url:
            logger.info(f"Connecting to Qdrant Cloud: {qdrant_url}")
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=api_key,
                timeout=60,
            )
            self.local_mode = False
        else:
            logger.info("Connecting to local Qdrant")
            from vectorstore.qdrant_store import qdrant_store
            self.client = qdrant_store.client
            self.local_mode = True

    def search(self, query_vector, limit=5, score_threshold=0.3, collection_name=None):
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def upsert_vectors(self, vectors, payloads, ids, collection_name=None):
        try:
            if self.local_mode:
                from qdrant_client.http.models import PointStruct
                points = []
                for id_val, vector, payload in zip(ids, vectors, payloads):
                    points.append(
                        PointStruct(
                            id=str(id_val),
                            vector=vector,
                            payload=payload,
                        )
                    )
                self.client.upsert(
                    collection_name=collection_name,
                    points=points,
                )
                logger.info(f"Upserted {len(points)} vectors to Qdrant Cloud")
                return True
            else:
                from vectorstore.qdrant_store import qdrant_store
                return qdrant_store.upsert_vectors(vectors, payloads, ids, collection_name)
        except Exception as e:
            logger.error(f"Upsert error: {e}")
            return False


qdrant_cloud_store = QdrantCloudStore()
