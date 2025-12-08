"""
Debug endpoint for troubleshooting RAG pipeline.

Provides detailed diagnostics for each component.
"""

import logging
from fastapi import APIRouter, HTTPException
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.services.llm import LLMService
from src.services.conversation import ConversationService
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/debug/components")
async def debug_components():
    """Test each RAG component individually."""
    results = {
        "config": {
            "collection_name": settings.qdrant_collection_name,
            "openai_model": settings.openai_chat_model,
            "embedding_model": settings.openai_embedding_model,
        },
        "tests": {}
    }

    # Test 1: Embedding Service
    try:
        embedding_service = EmbeddingService()
        test_embedding = await embedding_service.generate_embedding("test query")
        results["tests"]["embedding"] = {
            "status": "ok",
            "dimension": len(test_embedding)
        }
    except Exception as e:
        results["tests"]["embedding"] = {
            "status": "error",
            "error": str(e)
        }

    # Test 2: Vector Store - Collection Check
    try:
        vector_store = VectorStoreService()
        # Try to check if collection exists
        results["tests"]["vector_store_init"] = {"status": "ok"}
    except Exception as e:
        results["tests"]["vector_store_init"] = {
            "status": "error",
            "error": str(e)
        }

    # Test 3: Vector Store - Search
    try:
        if results["tests"]["embedding"]["status"] == "ok":
            search_results = await vector_store.search(
                query_embedding=test_embedding,
                top_k=1,
                score_threshold=0.0
            )
            results["tests"]["vector_store_search"] = {
                "status": "ok",
                "results_count": len(search_results)
            }
        else:
            results["tests"]["vector_store_search"] = {
                "status": "skipped",
                "reason": "embedding test failed"
            }
    except Exception as e:
        results["tests"]["vector_store_search"] = {
            "status": "error",
            "error": str(e)
        }

    # Test 4: Database
    try:
        conversation_service = ConversationService()
        session_id = await conversation_service.create_session()
        results["tests"]["database"] = {
            "status": "ok",
            "session_created": str(session_id)
        }
    except Exception as e:
        results["tests"]["database"] = {
            "status": "error",
            "error": str(e)
        }

    # Test 5: LLM Service
    try:
        llm_service = LLMService()
        # Don't actually call LLM to save costs, just check initialization
        results["tests"]["llm_init"] = {"status": "ok"}
    except Exception as e:
        results["tests"]["llm_init"] = {
            "status": "error",
            "error": str(e)
        }

    return results


@router.get("/debug/vector-store-stats")
async def debug_vector_store_stats():
    """Get detailed vector store statistics."""
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Get collection info
        try:
            collection_info = client.get_collection(settings.qdrant_collection_name)
            return {
                "status": "ok",
                "collection_name": settings.qdrant_collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else None,
            }
        except Exception as e:
            return {
                "status": "error",
                "collection_name": settings.qdrant_collection_name,
                "error": f"Collection not found or error: {str(e)}"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
