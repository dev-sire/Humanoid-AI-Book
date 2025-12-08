"""
Conversation persistence service.

Manages chat sessions and messages in Postgres database.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    CheckConstraint,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import select, func
from src.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class ChatSessionModel(Base):
    """SQLAlchemy model for chat_sessions table."""

    __tablename__ = "chat_sessions"

    session_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    messages = relationship("ChatMessageModel", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("last_activity_at >= created_at", name="chk_activity_after_creation"),
        Index("idx_sessions_last_activity", "last_activity_at"),
        Index("idx_sessions_created", "created_at"),
    )


class ChatMessageModel(Base):
    """SQLAlchemy model for chat_messages table."""

    __tablename__ = "chat_messages"

    message_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    selected_text = Column(Text, nullable=True)
    context_used = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    session = relationship("ChatSessionModel", back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="chk_valid_role"),
        CheckConstraint("LENGTH(content) >= 1 AND LENGTH(content) <= 10000", name="chk_content_length"),
        Index("idx_messages_session", "session_id"),
        Index("idx_messages_created", "created_at"),
        Index("idx_messages_role", "role"),
    )


class ConversationService:
    """Service for managing conversations in Postgres."""

    def __init__(self):
        """Initialize database connection."""
        # Convert postgresql:// to postgresql+asyncpg:// for SQLAlchemy async
        # Remove sslmode/channel_binding parameters as asyncpg doesn't support them
        import re
        db_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        db_url = re.sub(r'[?&](sslmode|channel_binding)=[^&]*', '', db_url)
        # Clean up any trailing ? or &
        db_url = re.sub(r'[?&]$', '', db_url)
        self.engine = create_async_engine(
            db_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=False,
            connect_args={"ssl": "require"},
        )
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create database tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

    async def create_session(self) -> UUID:
        """
        Create a new chat session.

        Returns:
            New session ID
        """
        try:
            async with self.async_session() as session:
                new_session = ChatSessionModel()
                session.add(new_session)
                await session.commit()
                logger.info(f"Created session: {new_session.session_id}")
                return new_session.session_id

        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise

    async def get_session(self, session_id: UUID) -> Optional[ChatSessionModel]:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session model or None if not found
        """
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
                )
                return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            return None

    async def save_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        selected_text: Optional[str] = None,
        context_used: Optional[Dict] = None,
    ) -> UUID:
        """
        Save a message to the database.

        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            selected_text: Optional selected text
            context_used: Optional context metadata

        Returns:
            Message ID
        """
        try:
            async with self.async_session() as session:
                message = ChatMessageModel(
                    session_id=session_id,
                    role=role,
                    content=content,
                    selected_text=selected_text,
                    context_used=context_used,
                )
                session.add(message)
                await session.commit()
                logger.info(f"Saved {role} message to session {session_id}")
                return message.message_id

        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            raise

    async def get_conversation_history(self, session_id: UUID) -> List[Dict]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session ID

        Returns:
            List of messages in chronological order
        """
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(ChatMessageModel)
                    .where(ChatMessageModel.session_id == session_id)
                    .order_by(ChatMessageModel.created_at.asc())
                )
                messages = result.scalars().all()

                return [
                    {
                        "message_id": str(msg.message_id),
                        "role": msg.role,
                        "content": msg.content,
                        "selected_text": msg.selected_text,
                        "context_used": msg.context_used,
                        "created_at": msg.created_at.isoformat(),
                    }
                    for msg in messages
                ]

        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            raise

    async def check_health(self) -> bool:
        """
        Check if database is accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            async with self.async_session() as session:
                await session.execute(select(func.count()).select_from(ChatSessionModel))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
