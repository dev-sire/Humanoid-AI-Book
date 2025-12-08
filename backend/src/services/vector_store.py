"""
Qdrant vector store service.

Manages vector search operations using Qdrant Cloud.
"""

import logging
from typing import List, Dict, Any
from uuid import UUID, uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint,
    Filter,
)
from src.config import settings
from src.models.document import ChunkPayload

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for vector search using Qdrant."""

    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        # 🔑 CRITICAL CHANGE: Use the new Gemini dimension setting
        # This fixes the AttributeError: 'Settings' object has no attribute 'openai_embedding_dimension'
        self.dimension = settings.gemini_embedding_dimension

    async def ensure_collection_exists(self) -> None:
        """
        Create collection if it doesn't exist.

        Creates a collection with cosine distance metric and configured dimensions.
        """
        try:
            # Note: This logic correctly uses self.dimension, which is now 3072.
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise

    async def upsert_chunks(
        self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> None:
        """
        Upsert document chunks with embeddings to Qdrant.
        ...
        """
        try:
            points = []
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload=chunk,
                )
                points.append(point)

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            logger.info(f"Upserted {len(points)} chunks to Qdrant")

        except Exception as e:
            logger.error(f"Failed to upsert chunks: {str(e)}")
            raise

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks.
        ...
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
            )

            chunks = []
            for result in results:
                chunk = {
                    "title": result.payload.get("title", "Untitled"),
                    "file_path": result.payload.get("file_path", ""),
                    "chunk_text": result.payload.get("chunk_text", ""),
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "total_chunks": result.payload.get("total_chunks", 1),
                    "relevance_score": result.score,
                }
                chunks.append(chunk)

            logger.info(f"Found {len(chunks)} chunks above threshold {score_threshold}")
            return chunks

        except Exception as e:
            logger.error(f"Failed to search vector store: {str(e)}")
            raise

    async def check_health(self) -> bool:
        """
        Check if Qdrant is accessible.
        ...
        """
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        ...
        """
        try:
            # We must use the synchronous client methods here as QdrantClient is not async by default.
            # However, the user's method is marked async, which is non-standard for QdrantClient methods.
            # Assuming the underlying environment handles this or the user wraps the QdrantClient methods 
            # with run_in_executor if true asynchronous calls are required in the real setup.
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {}

    async def delete_collection(self) -> bool:
        """
        Delete the collection.
        ...
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False