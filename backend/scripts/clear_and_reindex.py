"""
Clear Qdrant collection and reindex all documents.

This script deletes the existing collection and reindexes all documentation.
"""

import asyncio
import logging
import sys
from pathlib import Path
# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.vector_store import VectorStoreService
from index_docs import index_documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def clear_and_reindex():
    """Clear the collection and reindex all documents."""
    vector_store = VectorStoreService()

    # Step 1: Delete existing collection
    logger.info("Deleting existing collection...")
    success = await vector_store.delete_collection()
    if success:
        logger.info("Collection deleted successfully")
    else:
        logger.warning("Collection deletion failed or collection didn't exist")

    # Step 2: Reindex documents
    logger.info("Starting reindexing...")
    docs_dir = Path(__file__).parent.parent.parent / "book" / "docs"
    await index_documents(docs_dir)

    logger.info("Clear and reindex complete!")


if __name__ == "__main__":
    asyncio.run(clear_and_reindex())
