"""
Documentation indexing script.

Processes markdown files, generates embeddings, and uploads to Qdrant.
"""

import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Dict
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.services.embedding import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.utils.markdown import (
    extract_frontmatter,
    markdown_to_text,
    chunk_text,
    get_title_from_frontmatter,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def index_documents(docs_dir: str, file_pattern: str = "**/*.md*"):
    """
    Index all markdown documents in the specified directory.

    Args:
        docs_dir: Path to documentation directory
        file_pattern: Glob pattern for matching files (default: **/*.md*)
    """
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        logger.error(f"Documentation directory not found: {docs_dir}")
        return

    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService()

    # Ensure collection exists
    await vector_store.ensure_collection_exists()

    # Find all markdown files
    markdown_files = list(docs_path.glob(file_pattern))
    logger.info(f"Found {len(markdown_files)} markdown files")

    total_chunks = 0

    for file_path in markdown_files:
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title and convert to text
            title = get_title_from_frontmatter(content, fallback=file_path.stem)
            text = markdown_to_text(content)

            if not text.strip():
                logger.warning(f"Skipping empty file: {file_path}")
                continue

            # Chunk text
            chunks = chunk_text(
                text,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )

            logger.info(f"Processing {file_path.name}: {len(chunks)} chunks")

            # Prepare chunk metadata
            file_path_relative = str(file_path.relative_to(docs_path))
            chunk_metadata_list = [
                {
                    "title": title,
                    "file_path": file_path_relative,
                    "chunk_text": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
                for i, chunk in enumerate(chunks)
            ]

            # Generate embeddings in batch
            embeddings = await embedding_service.generate_embeddings_batch(chunks)

            # Upsert to Qdrant
            await vector_store.upsert_chunks(chunk_metadata_list, embeddings)

            total_chunks += len(chunks)
            logger.info(f"Indexed {file_path.name} ({len(chunks)} chunks)")

        except Exception as e:
            logger.error(f"Failed to index {file_path}: {str(e)}")
            continue

    logger.info(f"Indexing complete: {len(markdown_files)} files, {total_chunks} chunks")

    # Get collection info
    collection_info = await vector_store.get_collection_info()
    logger.info(f"Collection stats: {collection_info}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index documentation for RAG chatbot")
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="../../docs",
        help="Path to documentation directory (default: ../../docs)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.md*",
        help="File pattern to match (default: **/*.md*)",
    )

    args = parser.parse_args()

    logger.info("Starting documentation indexing...")
    await index_documents(args.docs_dir, args.pattern)
    logger.info("Indexing complete")


if __name__ == "__main__":
    asyncio.run(main())
