"""
Configuration management for RAG chatbot backend.

Loads environment variables using Pydantic Settings for type-safe configuration.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 💎 Gemini Configuration (replaces OpenAI)
    gemini_api_key: str = Field(..., description="Gemini API key")
    gemini_embedding_model: str = Field(
        default="gemini-embedding-001", description="Gemini embedding model"
    )
    gemini_chat_model: str = Field(default="gemini-2.5-flash", description="Gemini chat model")
    # NOTE: gemini-embedding-001 has a dimension of 3072
    gemini_embedding_dimension: int = Field(default=3072, description="Embedding vector dimension")

    # --- Configuration from original script (Kept as is) ---
    
    # Qdrant Configuration
    qdrant_url: str = Field(..., description="Qdrant cluster URL")
    qdrant_api_key: str = Field(..., description="Qdrant API key")
    qdrant_collection_name: str = Field(
        default="ai_native_book", description="Qdrant collection name"
    )

    # Neon Postgres Configuration
    database_url: str = Field(..., description="PostgreSQL connection URL")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(
        default=20, description="Max overflow connections beyond pool size"
    )

    # Application Configuration
    app_env: str = Field(default="development", description="Application environment")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001", description="Allowed CORS origins"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    session_expiry_days: int = Field(default=7, description="Session expiration in days")

    # RAG Configuration
    chunk_size: int = Field(default=1000, description="Document chunk size in words")
    chunk_overlap: int = Field(default=200, description="Chunk overlap in words")
    top_k_results: int = Field(default=5, description="Number of top results to retrieve")
    similarity_threshold: float = Field(
        default=0.6, description="Minimum similarity threshold for retrieval"
    )
    max_query_length: int = Field(default=1000, description="Maximum query length in characters")
    max_conversation_context: int = Field(
        default=6, description="Max conversation history messages for context"
    )

    # Rate Limiting
    rate_limit_queries_per_hour: int = Field(
        default=60, description="Max queries per hour per IP"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()