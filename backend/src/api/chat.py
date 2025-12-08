"""
Chat endpoint.

Handles user queries and returns AI-generated responses with sources.
"""

import logging
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException
from src.models.chat import ChatRequest, ChatResponse
from src.services.rag_service import RAGService
from src.utils.sanitization import sanitize_query, sanitize_selected_text, validate_session_id, detect_prompt_injection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user query and return AI-generated response with sources.

    Args:
        request: Chat request with message, optional session_id, optional selected_text

    Returns:
        Chat response with session_id, message, sources, and timestamp

    Status Codes:
        200: Success
        400: Invalid input (validation error, prompt injection detected)
        429: Rate limit exceeded
        500: Server error
    """
    try:
        # Sanitize and validate query
        try:
            sanitized_query = sanitize_query(request.message, max_length=1000)
        except ValueError as e:
            logger.warning(f"Query validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        # Detect prompt injection
        if detect_prompt_injection(sanitized_query):
            logger.warning(f"Prompt injection detected: {sanitized_query[:100]}")
            raise HTTPException(
                status_code=400,
                detail="Invalid query: Your message contains patterns that could be harmful.",
            )

        # Sanitize selected text if present
        sanitized_selected_text = None
        if request.selected_text:
            sanitized_selected_text = sanitize_selected_text(
                request.selected_text, min_length=1, max_length=1000
            )
            if sanitized_selected_text is None:
                logger.warning("Selected text validation failed")
                raise HTTPException(
                    status_code=400,
                    detail="Selected text must be between 1-1000 characters",
                )

        # Validate session ID if provided
        session_id = None
        if request.session_id:
            if not validate_session_id(request.session_id):
                logger.warning(f"Invalid session ID format: {request.session_id}")
                raise HTTPException(status_code=400, detail="Invalid session ID format")
            session_id = UUID(request.session_id)

        # Process query through RAG pipeline
        rag_service = RAGService()
        response_text, sources, final_session_id = await rag_service.process_query(
            query=sanitized_query,
            session_id=session_id,
            selected_text=sanitized_selected_text,
        )

        logger.info(f"Successfully processed query for session {final_session_id}")

        return ChatResponse(
            session_id=str(final_session_id),
            message=response_text,
            sources=sources,
            timestamp=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again.",
        )
