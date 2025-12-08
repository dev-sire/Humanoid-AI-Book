"""
Gemini embeddings service.

Generates embeddings for queries and documents using the Gemini API.
"""

import logging
from typing import List
# 1. CHANGE: Import the new Google Generative AI SDK
from google import genai
from google.genai import types as genai_types
from src.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using the Gemini API."""

    def __init__(self):
        """Initialize Gemini client."""
        # 2. CHANGE: Initialize the asynchronous Gemini Client (Gemini SDK)
        self.client = genai.Client(api_key=settings.gemini_api_key).aio
        self.model = settings.gemini_embedding_model
        # The dimension property is still useful for vector database initialization,
        # but is no longer required as a parameter in the API call itself.
        self.dimension = settings.gemini_embedding_dimension 

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text, optimized for retrieval query.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            Exception: If API call fails
        """
        try:
            # 3. CRITICAL CHANGE: Use client.models.embed_content for single input
            # Use RETRIEVAL_QUERY for the query you want to search with
            response = await self.client.models.embed_content(
                model=self.model,
                contents=text, # Pass single string directly
                config=genai_types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    # Optional: Use output_dimensionality to truncate the vector if needed, 
                    # but we use the full dimension (3072) by default.
                    # output_dimensionality=self.dimension 
                ),
            )
            # 4. CHANGE: Extract the embedding from the new response object structure
            embedding = response.embeddings[0].values
            logger.info(f"Generated query embedding (dimension: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch, optimized for documents.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors

        Raises:
            Exception: If API call fails
        """
        try:
            # 5. CRITICAL CHANGE: Use client.models.embed_content for batch input
            # Use RETRIEVAL_DOCUMENT for the documents you are indexing
            response = await self.client.models.embed_content(
                model=self.model,
                contents=texts, # Pass list of strings directly
                config=genai_types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    # Optional: output_dimensionality=self.dimension
                ),
            )
            # 6. CHANGE: Extract embeddings list from the response
            embeddings = [item.values for item in response.embeddings]
            logger.info(f"Generated {len(embeddings)} document embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings batch: {str(e)}")
            raise