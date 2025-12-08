# Data Model: RAG Chatbot Integration

**Feature**: 011-rag-chatbot-integration
**Date**: 2025-12-01
**Purpose**: Define all entities, relationships, and validation rules for the RAG chatbot system

---

## Entity Relationship Diagram

```
┌─────────────────┐
│  ChatSession    │
│─────────────────│
│ session_id (PK) │◄─────┐
│ created_at      │      │
│ last_activity_at│      │
└─────────────────┘      │
                         │ 1:N
                    ┌────┴────────────┐
                    │  ChatMessage    │
                    │─────────────────│
                    │ message_id (PK) │
                    │ session_id (FK) │
                    │ role            │
                    │ content         │
                    │ selected_text   │
                    │ context_used    │
                    │ created_at      │
                    └─────────────────┘

┌──────────────────┐
│  DocumentChunk   │ (stored in Qdrant)
│──────────────────│
│ chunk_id (PK)    │
│ title            │
│ file_path        │
│ chunk_text       │
│ chunk_index      │
│ total_chunks     │
│ embedding[1536]  │
│ metadata (JSON)  │
└──────────────────┘
        │
        │ Retrieved by
        │ (ephemeral)
        ▼
┌──────────────────┐
│     Source       │ (transient entity)
│──────────────────│
│ title            │
│ file_path        │
│ relevance_score  │
│ excerpt          │
└──────────────────┘
```

---

## Entity Definitions

### 1. ChatSession

**Description**: Represents a conversation session between a user and the chatbot. Each session has a unique ID and tracks activity timestamps for expiration management.

**Storage**: Neon Serverless Postgres (`chat_sessions` table)

#### Fields

| Field Name        | Type      | Constraints                          | Description                              |
|-------------------|-----------|--------------------------------------|------------------------------------------|
| `session_id`      | UUID      | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the session        |
| `created_at`      | TIMESTAMP | NOT NULL, DEFAULT NOW()              | Timestamp when session was created       |
| `last_activity_at`| TIMESTAMP | NOT NULL, DEFAULT NOW()              | Timestamp of last user/assistant activity|

#### Relationships
- **Has Many**: ChatMessage (1:N relationship via session_id foreign key)

#### Validation Rules
- `session_id` must be a valid UUID (RFC 4122 format)
- `created_at` must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
- `last_activity_at` must be >= `created_at`
- `last_activity_at` is updated on every new message (user or assistant)

#### State Transitions
1. **Created**: Session is created when user sends first message (no session_id provided)
2. **Active**: Session is active while messages are being exchanged
3. **Expired**: Session expires after 7 days of inactivity (`last_activity_at < NOW() - INTERVAL '7 days'`)

#### Lifecycle Management
- **Creation**: Automatically created on first message if no session_id provided
- **Update**: `last_activity_at` updated on every message send/receive
- **Expiration**: Sessions older than 7 days are deleted (manual cleanup or cron job)
- **Deletion**: Cascade delete all associated ChatMessage records

---

### 2. ChatMessage

**Description**: Represents a single message in a conversation, sent by either the user or the assistant. Messages are immutable once created and store optional context (selected text, retrieved chunks).

**Storage**: Neon Serverless Postgres (`chat_messages` table)

#### Fields

| Field Name      | Type      | Constraints                                    | Description                                  |
|-----------------|-----------|------------------------------------------------|----------------------------------------------|
| `message_id`    | UUID      | PRIMARY KEY, DEFAULT gen_random_uuid()         | Unique identifier for the message            |
| `session_id`    | UUID      | FOREIGN KEY REFERENCES chat_sessions(session_id) ON DELETE CASCADE | Links message to session |
| `role`          | VARCHAR(20)| NOT NULL, CHECK (role IN ('user', 'assistant'))| Message sender role                          |
| `content`       | TEXT      | NOT NULL, LENGTH >= 1, LENGTH <= 10000         | Message text content                         |
| `selected_text` | TEXT      | NULLABLE, LENGTH >= 1, LENGTH <= 1000          | User-selected page text (user messages only) |
| `context_used`  | JSONB     | NULLABLE                                        | Retrieved chunks used for answer (assistant only) |
| `created_at`    | TIMESTAMP | NOT NULL, DEFAULT NOW()                        | Timestamp when message was created           |

#### Relationships
- **Belongs To**: ChatSession (N:1 relationship via session_id foreign key)

#### Validation Rules
- `message_id` must be a valid UUID (RFC 4122 format)
- `session_id` must reference an existing ChatSession
- `role` must be exactly 'user' or 'assistant' (case-sensitive)
- `content` length must be between 1 and 10,000 characters
- `selected_text` (if provided) length must be between 1 and 1,000 characters
- `created_at` must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)

#### State Transitions
- **N/A**: Messages are immutable once created (no state transitions)

#### Lifecycle Management
- **Creation**: Created when user sends message or assistant responds
- **Update**: Never updated (immutable)
- **Deletion**: Deleted when parent ChatSession is deleted (CASCADE)

#### Context Schema (`context_used` field)
```json
{
  "chunks": [
    {
      "title": "string",
      "file_path": "string",
      "relevance_score": 0.85,
      "excerpt": "string"
    }
  ],
  "retrieval_timestamp": "2025-12-01T12:00:00.000Z"
}
```

---

### 3. DocumentChunk

**Description**: Represents a searchable chunk of documentation content with its embedding vector. Chunks are created during document indexing and stored in the vector database for semantic search.

**Storage**: Qdrant Cloud (vector database collection `documentation_chunks`)

#### Fields

| Field Name      | Type       | Constraints                  | Description                                |
|-----------------|------------|------------------------------|--------------------------------------------|
| `chunk_id`      | UUID       | PRIMARY KEY (Qdrant point ID)| Unique identifier for the chunk            |
| `title`         | STRING     | NOT NULL, LENGTH >= 1        | Document title (from frontmatter)          |
| `file_path`     | STRING     | NOT NULL, UNIQUE per chunk   | Relative path to source .md/.mdx file      |
| `chunk_text`    | STRING     | NOT NULL, LENGTH >= 100      | Actual text content of the chunk           |
| `chunk_index`   | INTEGER    | NOT NULL, >= 0               | Index of chunk within document (0-based)   |
| `total_chunks`  | INTEGER    | NOT NULL, >= 1               | Total number of chunks in source document  |
| `embedding`     | VECTOR[1536]| NOT NULL                    | 1536-dimensional embedding vector          |
| `metadata`      | JSON       | NULLABLE                     | Additional metadata (frontmatter, tags)    |

#### Relationships
- **N/A**: No explicit relationships (vector database stores flat collection)
- Logically related to source document via `file_path`

#### Validation Rules
- `chunk_id` must be a valid UUID (RFC 4122 format)
- `title` must not be empty string
- `file_path` must be relative path starting with `docs/` (e.g., `docs/ros2/fundamentals.md`)
- `chunk_text` must be at least 100 characters (prevent indexing of trivial chunks)
- `chunk_index` must be >= 0 and < `total_chunks`
- `total_chunks` must be >= 1
- `embedding` must be exactly 1536 dimensions (OpenAI text-embedding-3-small output)

#### State Transitions
1. **Indexed**: Chunk is created during initial documentation indexing
2. **Active**: Chunk is available for semantic search
3. **Updated**: Chunk is re-indexed when source document changes
4. **Deleted**: Chunk is removed when source document is deleted

#### Lifecycle Management
- **Creation**: Created during `index_docs.py` script execution
- **Update**: Re-created (delete + insert) when source document changes
- **Deletion**: Manually deleted or when source document is removed from `docs/` directory

#### Metadata Schema (`metadata` field)
```json
{
  "frontmatter": {
    "sidebar_position": 1,
    "tags": ["ROS2", "fundamentals"]
  },
  "indexed_at": "2025-12-01T12:00:00.000Z"
}
```

---

### 4. Source (Transient Entity)

**Description**: Represents a citation returned with chatbot answers. Sources are ephemeral entities derived from DocumentChunk during retrieval and are NOT persisted in any database.

**Storage**: In-memory only (transient, exists only in API response lifecycle)

#### Fields

| Field Name       | Type    | Constraints              | Description                               |
|------------------|---------|--------------------------|-------------------------------------------|
| `title`          | STRING  | NOT NULL, LENGTH >= 1    | Document title (from DocumentChunk)       |
| `file_path`      | STRING  | NOT NULL                 | Relative path to source document          |
| `relevance_score`| FLOAT   | NOT NULL, 0.0 <= x <= 1.0| Cosine similarity score (Qdrant search)   |
| `excerpt`        | STRING  | NOT NULL, LENGTH <= 500  | Text excerpt from chunk (first 500 chars) |

#### Relationships
- **Derived From**: DocumentChunk (during vector search retrieval)
- Not persisted (no database relationships)

#### Validation Rules
- `title` must not be empty string
- `file_path` must be relative path starting with `docs/`
- `relevance_score` must be between 0.0 and 1.0 (inclusive)
- `excerpt` must be truncated to 500 characters max (with "..." if truncated)

#### State Transitions
- **N/A**: Sources are ephemeral (created per query, discarded after response)

#### Lifecycle Management
- **Creation**: Created during RAG pipeline retrieval step (top 5 DocumentChunks)
- **Usage**: Included in API response to frontend, optionally stored in `context_used` field of ChatMessage
- **Deletion**: Garbage collected after API response is sent

---

## Database Indexes

### Postgres (chat_sessions, chat_messages)

```sql
-- Index on session_id for fast message lookups
CREATE INDEX idx_messages_session ON chat_messages(session_id);

-- Index on last_activity_at for efficient session expiration queries
CREATE INDEX idx_sessions_last_activity ON chat_sessions(last_activity_at);

-- Optional: Index on created_at for chronological queries
CREATE INDEX idx_messages_created ON chat_messages(created_at);
```

### Qdrant (documentation_chunks)

```json
{
  "collection_name": "documentation_chunks",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "indexes": [
    {
      "field": "file_path",
      "type": "keyword"
    },
    {
      "field": "title",
      "type": "keyword"
    }
  ]
}
```

---

## Data Flow Diagrams

### Indexing Flow (Document → DocumentChunk)

```
┌──────────────┐
│ Markdown File│
│ (docs/*.md)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Parse Frontmatter        │
│ Extract: title, metadata │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Clean Markdown           │
│ Remove: code blocks, etc │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Chunk Text               │
│ 1000 words, 200 overlap  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Generate Embeddings      │
│ OpenAI text-emb-3-small  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Store in Qdrant          │
│ DocumentChunk collection │
└──────────────────────────┘
```

### Query Flow (User Query → Chatbot Response)

```
┌──────────────┐
│ User Query   │
│ + selected_  │
│   text       │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Sanitize Input           │
│ Check prompt injection   │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Generate Query Embedding │
│ OpenAI text-emb-3-small  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Vector Search (Qdrant)   │
│ Top 5 chunks, cosine sim │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Filter by Threshold      │
│ score >= 0.7             │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Build Prompt             │
│ System + Context + Query │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ LLM Generation           │
│ OpenAI GPT-4o-mini       │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Save ChatMessage         │
│ user + assistant messages│
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Return Response          │
│ + Source citations       │
└──────────────────────────┘
```

---

## Validation & Constraints Summary

### Input Validation (API Layer)

| Field           | Min | Max   | Pattern/Rules                              |
|-----------------|-----|-------|--------------------------------------------|
| User query      | 1   | 1000  | No control chars, sanitize patterns        |
| Selected text   | 1   | 1000  | Optional, plain text only                  |
| Session ID      | -   | -     | Valid UUID v4 format                       |

### Storage Constraints

| Entity          | Postgres Table       | Max Records | Retention   |
|-----------------|----------------------|-------------|-------------|
| ChatSession     | `chat_sessions`      | ~10,000     | 7 days      |
| ChatMessage     | `chat_messages`      | ~100,000    | 7 days      |
| DocumentChunk   | Qdrant collection    | ~10,000     | Until updated|

### Performance Constraints

| Operation                | Target   | Notes                              |
|--------------------------|----------|------------------------------------|
| Vector search (Qdrant)   | <50ms    | P95 latency for top-5 retrieval    |
| Postgres query           | <20ms    | Session + message fetches          |
| OpenAI embedding API     | <200ms   | Single query embedding             |
| OpenAI chat completion   | <1500ms  | GPT-4o-mini generation with context|
| Total response time      | <2000ms  | P95 end-to-end latency             |

---

## Schema Evolution Strategy

### Version 1.0 (Initial)
- Two Postgres tables: `chat_sessions`, `chat_messages`
- One Qdrant collection: `documentation_chunks`

### Future Considerations (Out of Scope)
- **Feedback table**: Store user ratings for chatbot responses (thumbs up/down)
- **Analytics table**: Track query patterns, popular topics, session durations
- **User table**: Add authentication and personalized conversation history
- **Multi-language support**: Add `language` field to DocumentChunk metadata

### Migration Strategy
- Use Alembic for Postgres schema migrations
- Qdrant schema changes require full re-indexing (no migration support)
- Version all schemas with creation date in documentation

---

## Summary

This data model defines four core entities:
1. **ChatSession**: Conversation session tracking (Postgres)
2. **ChatMessage**: Individual messages (Postgres)
3. **DocumentChunk**: Indexed documentation chunks with embeddings (Qdrant)
4. **Source**: Transient citation entity (in-memory only)

All validation rules, relationships, and lifecycle management strategies are clearly defined. The model supports the full RAG pipeline while adhering to constitutional requirements for data privacy (no PII storage), performance (<2s response time), and maintainability (clear schemas, explicit constraints).
