-- ============================================================================
-- RAG Chatbot Database Schema
-- ============================================================================
-- Database: Neon Serverless Postgres
-- Version: 1.0.0
-- Created: 2025-12-01
-- Description: Schema for RAG chatbot conversation storage
-- ============================================================================

-- Enable UUID extension for automatic UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: chat_sessions
-- ============================================================================
-- Purpose: Stores conversation sessions between users and the chatbot
-- Lifecycle: Created on first message, expires after 7 days of inactivity
-- Relationships: Has many chat_messages (1:N)
-- ============================================================================

CREATE TABLE IF NOT EXISTS chat_sessions (
    -- Primary key: unique session identifier
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Timestamp when session was created
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Timestamp of last activity (updated on every message)
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_activity_after_creation CHECK (last_activity_at >= created_at)
);

-- Index for efficient session expiration queries
CREATE INDEX idx_sessions_last_activity ON chat_sessions(last_activity_at);

-- Index for chronological queries
CREATE INDEX idx_sessions_created ON chat_sessions(created_at);

-- ============================================================================
-- TABLE: chat_messages
-- ============================================================================
-- Purpose: Stores individual messages in conversations
-- Lifecycle: Created when user sends message or assistant responds, immutable
-- Relationships: Belongs to chat_sessions (N:1)
-- ============================================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    -- Primary key: unique message identifier
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key: links message to session (cascade delete)
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,

    -- Message sender role: 'user' or 'assistant'
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),

    -- Message text content (1-10000 characters)
    content TEXT NOT NULL CHECK (LENGTH(content) >= 1 AND LENGTH(content) <= 10000),

    -- Optional: user-selected page text (1-1000 characters)
    selected_text TEXT CHECK (selected_text IS NULL OR (LENGTH(selected_text) >= 1 AND LENGTH(selected_text) <= 1000)),

    -- Optional: JSON object containing retrieved chunks used for answer (assistant messages only)
    -- Schema: { "chunks": [{"title": str, "file_path": str, "relevance_score": float, "excerpt": str}], "retrieval_timestamp": ISO8601 }
    context_used JSONB,

    -- Timestamp when message was created
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for fast message lookups by session
CREATE INDEX idx_messages_session ON chat_messages(session_id);

-- Index for chronological queries
CREATE INDEX idx_messages_created ON chat_messages(created_at);

-- Index for role-based queries (optional, for analytics)
CREATE INDEX idx_messages_role ON chat_messages(role);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function: Update last_activity_at timestamp when new message is added
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET last_activity_at = NEW.created_at
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Automatically update last_activity_at on message insert
CREATE TRIGGER trg_update_session_activity
AFTER INSERT ON chat_messages
FOR EACH ROW
EXECUTE FUNCTION update_session_activity();

-- ============================================================================
-- CLEANUP FUNCTIONS
-- ============================================================================

-- Function: Delete sessions older than 7 days (for manual or cron execution)
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS TABLE(deleted_count INTEGER) AS $$
DECLARE
    count INTEGER;
BEGIN
    -- Delete sessions with no activity in the last 7 days
    DELETE FROM chat_sessions
    WHERE last_activity_at < NOW() - INTERVAL '7 days';

    -- Get count of deleted rows
    GET DIAGNOSTICS count = ROW_COUNT;

    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;