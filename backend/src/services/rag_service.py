"""
RAG orchestration service.

Coordinates the RAG pipeline: embedding → retrieval → generation.
"""

import logging
from typing import List, Dict, Optional
from uuid import UUID
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.services.llm import LLMService
from src.services.conversation import ConversationService
from src.models.chat import Source
from src.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for orchestrating the RAG pipeline."""

    def __init__(self):
        """Initialize all component services."""
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.conversation_service = ConversationService()

    async def process_query(
        self,
        query: str,
        session_id: Optional[UUID] = None,
        selected_text: Optional[str] = None,
    ) -> tuple[str, List[Source], UUID]:
        """
        Process user query through RAG pipeline.

        Args:
            query: User query
            session_id: Optional existing session ID
            selected_text: Optional selected text from page

        Returns:
            Tuple of (response, sources, session_id)

        Raises:
            Exception: If any step in pipeline fails
        """
        try:
            # Step 1: Create or get session
            if session_id is None:
                session_id = await self.conversation_service.create_session()
                logger.info(f"Created new session: {session_id}")
            else:
                logger.info(f"Using existing session: {session_id}")

            # Step 2: Get conversation history
            conversation_history = await self.conversation_service.get_conversation_history(
                session_id
            )
            logger.info(f"Loaded {len(conversation_history)} previous messages")

            # Step 3: Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            logger.info("Generated query embedding")

            # Step 4: Search vector store
            retrieved_chunks = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=settings.top_k_results,
                score_threshold=settings.similarity_threshold,
            )
            logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")

            # Step 5: Check if we have relevant results
            if not retrieved_chunks:
                response = (
                    "I don't have information about that in the documentation. "
                    "I can only answer questions about Physical AI, robotics, ROS2, "
                    "and related topics covered in this book."
                )
                sources = []
            else:
                # Step 6: Generate response with LLM
                response = await self.llm_service.generate_response(
                    query=query,
                    retrieved_chunks=retrieved_chunks,
                    conversation_history=conversation_history,
                    selected_text=selected_text,
                )
                logger.info("Generated LLM response")

                # Step 7: Format sources (deduplicate by file_path, keeping highest score)
                seen_files = {}
                for chunk in retrieved_chunks:
                    file_path = chunk["file_path"]
                    # Keep only the highest-scoring chunk for each file
                    if file_path not in seen_files or chunk["relevance_score"] > seen_files[file_path]["relevance_score"]:
                        seen_files[file_path] = chunk

                # Create Source objects from deduplicated chunks
                sources = [
                    Source(
                        title=chunk["title"],
                        file_path=chunk["file_path"],
                        relevance_score=chunk["relevance_score"],
                        excerpt=chunk["chunk_text"][:500],  # Limit excerpt length
                    )
                    for chunk in seen_files.values()
                ]
                # Sort by relevance score (highest first)
                sources.sort(key=lambda x: x.relevance_score, reverse=True)

            # Step 8: Save user message
            await self.conversation_service.save_message(
                session_id=session_id,
                role="user",
                content=query,
                selected_text=selected_text,
            )

            # Step 9: Save assistant message with context
            context_metadata = {
                "chunks": [
                    {
                        "title": chunk["title"],
                        "file_path": chunk["file_path"],
                        "relevance_score": chunk["relevance_score"],
                    }
                    for chunk in retrieved_chunks
                ],
                "retrieval_count": len(retrieved_chunks),
            }

            await self.conversation_service.save_message(
                session_id=session_id,
                role="assistant",
                content=response,
                context_used=context_metadata,
            )

            logger.info(f"RAG pipeline completed for session {session_id}")
            return response, sources, session_id

        except Exception as e:
            logger.error(f"RAG pipeline failed: {str(e)}")
            raise

    async def get_session_history(self, session_id: UUID) -> List[Dict]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session ID

        Returns:
            List of messages
        """
        return await self.conversation_service.get_conversation_history(session_id)

    async def check_health(self) -> Dict[str, str]:
        """
        Check health of all services.

        Returns:
            Dictionary with service statuses
        """
        health = {}

        # Check Qdrant
        qdrant_healthy = await self.vector_store.check_health()
        health["qdrant"] = "up" if qdrant_healthy else "down"

        # Check Postgres
        postgres_healthy = await self.conversation_service.check_health()
        health["postgres"] = "up" if postgres_healthy else "down"

        # Check OpenAI
        openai_healthy = await self.llm_service.check_health()
        health["openai"] = "up" if openai_healthy else "down"

        return health
