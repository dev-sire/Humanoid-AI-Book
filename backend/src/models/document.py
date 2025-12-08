"""
Document domain models.

Pydantic models for document chunks and sources in the vector database.
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Document chunk stored in vector database."""

    chunk_id: UUID = Field(description="Unique chunk identifier")
    title: str = Field(description="Document title")
    file_path: str = Field(description="File path relative to docs/")
    chunk_text: str = Field(description="Chunk text content")
    chunk_index: int = Field(ge=0, description="Chunk index in document")
    total_chunks: int = Field(gt=0, description="Total chunks in document")
    embedding: Optional[list[float]] = Field(
        default=None, description="Embedding vector (1536 dimensions)"
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    model_config = {"from_attributes": True}


class DocumentMetadata(BaseModel):
    """Metadata for document indexing."""

    file_path: str = Field(description="File path relative to docs/")
    title: str = Field(description="Document title")
    sidebar_position: Optional[int] = Field(default=None, description="Sidebar position from frontmatter")
    last_modified: Optional[str] = Field(default=None, description="Last modified timestamp")


class ChunkPayload(BaseModel):
    """Payload for storing chunks in Qdrant."""

    title: str = Field(description="Document title")
    file_path: str = Field(description="File path")
    chunk_index: int = Field(description="Chunk index")
    total_chunks: int = Field(description="Total chunks")
    chunk_text: str = Field(description="Chunk text")
