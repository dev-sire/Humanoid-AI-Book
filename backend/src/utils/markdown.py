"""
Markdown parsing utilities for document indexing.

Provides functions to extract text from markdown/MDX files and clean content
for embedding generation.
"""

import re
from typing import Dict, Any
from bs4 import BeautifulSoup
import markdown


def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content with optional frontmatter

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    frontmatter = {}
    body = content

    # Check if content starts with frontmatter delimiter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # Parse YAML frontmatter (simple key-value pairs)
            frontmatter_text = parts[1].strip()
            for line in frontmatter_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"').strip("'")
            body = parts[2].strip()

    return frontmatter, body


def remove_code_blocks(text: str) -> str:
    """
    Remove code blocks from markdown text.

    Args:
        text: Markdown text

    Returns:
        Text with code blocks removed
    """
    # Remove fenced code blocks (```...```)
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Remove inline code (`...`)
    text = re.sub(r"`[^`]*`", "", text)

    return text


def markdown_to_text(content: str) -> str:
    """
    Convert markdown to plain text for embedding generation.

    Args:
        content: Markdown content

    Returns:
        Plain text with markdown formatting removed
    """
    # Remove frontmatter
    _, body = extract_frontmatter(content)

    # Remove code blocks
    body = remove_code_blocks(body)

    # Convert markdown to HTML
    html = markdown.markdown(body, extensions=["extra", "nl2br"])

    # Extract text from HTML
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text
        chunk_size: Size of each chunk in words
        overlap: Number of words to overlap between chunks

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []

    if len(words) <= chunk_size:
        return [text]

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        # Move start forward by (chunk_size - overlap)
        start += chunk_size - overlap

        # Prevent infinite loop if overlap >= chunk_size
        if overlap >= chunk_size:
            start += 1

    return chunks


def get_title_from_frontmatter(content: str, fallback: str = "Untitled") -> str:
    """
    Extract title from markdown frontmatter.

    Args:
        content: Markdown content with frontmatter
        fallback: Default title if none found

    Returns:
        Document title
    """
    frontmatter, _ = extract_frontmatter(content)
    return frontmatter.get("title", fallback)
