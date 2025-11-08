"""
Utility functions for SDK
"""

import base64
import re
from typing import Dict, List, Tuple, Union


# ============================================================================
# RAG Helper Functions
# ============================================================================


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Chunk text into smaller pieces for embedding

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in words (default: 500)
        overlap: Number of overlapping words between chunks (default: 50)

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    # Split text into words
    words = text.strip().split()

    if len(words) <= chunk_size:
        return [text]

    chunks: List[str] = []
    current_index = 0

    while current_index < len(words):
        # Extract chunk
        chunk = words[current_index : current_index + chunk_size]
        chunks.append(" ".join(chunk))

        # Move to next chunk with overlap
        current_index += chunk_size - overlap

        # Ensure we don't go past the end
        if current_index >= len(words):
            break

    return chunks


def encode_file_to_base64(file_content: Union[bytes, bytearray]) -> str:
    """
    Convert file to base64 encoding for upload

    Args:
        file_content: File content as bytes

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(file_content).decode("utf-8")


def validate_embedding_dimensions(expected: int, actual: int) -> None:
    """
    Validate embedding dimensions match

    Args:
        expected: Expected dimensions
        actual: Actual dimensions

    Raises:
        ValueError: If dimensions don't match
    """
    if expected != actual:
        raise ValueError(
            f"Embedding dimension mismatch: expected {expected}, got {actual}. "
            f"Ensure the embedding model matches the collection's embedding model."
        )


def get_similarity_threshold(quality: str) -> float:
    """
    Calculate similarity threshold for RAG search

    Args:
        quality: Quality level: 'high', 'medium', or 'low'

    Returns:
        Similarity threshold (0-1)
    """
    thresholds = {"high": 0.8, "medium": 0.7, "low": 0.5}
    return thresholds.get(quality.lower(), 0.7)


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text (rough approximation)

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters (or 0.75 words)
    chars = len(text)
    return (chars + 3) // 4  # Round up


def truncate_to_token_limit(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within token limit

    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens

    Returns:
        Truncated text
    """
    estimated_tokens = estimate_token_count(text)

    if estimated_tokens <= max_tokens:
        return text

    # Calculate how many characters to keep
    max_chars = max_tokens * 4
    return text[:max_chars] + "..."


def format_rag_context(
    results: List[Dict[str, any]], max_context_length: int = 4000
) -> str:
    """
    Format RAG results as context string for injection into prompts

    Args:
        results: List of similarity search results
        max_context_length: Maximum context length in characters (default: 4000)

    Returns:
        Formatted context string
    """
    if not results:
        return ""

    context_parts: List[str] = []
    current_length = 0

    for i, result in enumerate(results):
        content = result.get("content", "")
        similarity = result.get("similarity", 0)

        part = f"[Document {i + 1}] (Relevance: {similarity * 100:.1f}%)\n{content}\n"

        # Check if adding this part exceeds max length
        if current_length + len(part) > max_context_length:
            # Truncate this part to fit
            remaining_length = max_context_length - current_length
            if remaining_length > 100:
                # Only add if we have significant space left
                context_parts.append(part[:remaining_length - 3] + "...")
            break

        context_parts.append(part)
        current_length += len(part)

    return "\n".join(context_parts)


# ============================================================================
# Variable Substitution Functions
# ============================================================================


def substitute_variables(template: str, variables: Dict[str, str]) -> str:
    """
    Substitute variables in a template string

    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary with variable values

    Returns:
        String with variables substituted
    """
    if not template:
        return template

    result = template

    # Find all variables in format {{variable_name}}
    pattern = re.compile(r"\{\{([^}]+)\}\}")
    matches = pattern.finditer(template)

    for match in matches:
        full_match = match.group(0)  # {{variable_name}}
        variable_name = match.group(1).strip()  # variable_name

        # Replace with value if found, otherwise keep placeholder
        value = variables.get(variable_name)
        if value is not None:
            result = result.replace(full_match, value)

    return result


def extract_variable_names(template: str) -> List[str]:
    """
    Extract variable names from a template string

    Args:
        template: Template string with {{variable}} placeholders

    Returns:
        List of variable names
    """
    if not template:
        return []

    pattern = re.compile(r"\{\{([^}]+)\}\}")
    matches = pattern.finditer(template)
    names: List[str] = []

    for match in matches:
        variable_name = match.group(1).strip()
        if variable_name not in names:
            names.append(variable_name)

    return names


def validate_variables(template: str, variables: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate that all required variables are provided

    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary with variable values

    Returns:
        Tuple of (valid, missing_variables)
    """
    required = extract_variable_names(template)
    provided = list(variables.keys())
    missing = [name for name in required if name not in provided]

    return (len(missing) == 0, missing)


def sanitize_variable_name(name: str) -> str:
    """
    Create a safe variable name (alphanumeric and underscores only)

    Args:
        name: Original name

    Returns:
        Sanitized name
    """
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)
