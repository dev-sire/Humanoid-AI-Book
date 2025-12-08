"""
Session history endpoint.

Retrieves conversation history for a given session.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException
from src.models.chat import SessionHistoryResponse, ChatMessage
from src.services.rag_service import RAGService
from src.utils.sanitization import validate_session_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.

    Args:
        session_id: Session ID (UUID)

    Returns:
        Session history with all messages in chronological order

    Status Codes:
        200: Success
        400: Invalid session ID format
        404: Session not found
        500: Server error
    """
    try:
        # Validate session ID format
        if not validate_session_id(session_id):
            logger.warning(f"Invalid session ID format: {session_id}")
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        session_uuid = UUID(session_id)

        # Get conversation history
        rag_service = RAGService()
        messages = await rag_service.get_session_history(session_uuid)

        if not messages:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert to ChatMessage models
        chat_messages = [
            ChatMessage(
                message_id=UUID(msg["message_id"]),
                session_id=session_uuid,
                role=msg["role"],
                content=msg["content"],
                selected_text=msg.get("selected_text"),
                context_used=msg.get("context_used"),
                created_at=msg["created_at"],
            )
            for msg in messages
        ]

        logger.info(f"Retrieved {len(chat_messages)} messages for session {session_id}")

        return SessionHistoryResponse(
            session_id=session_id,
            messages=chat_messages,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session history endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving session history.",
        )
