"""Token counting and text splitting utilities."""

from typing import List, Dict, Any
from . import patterns


def count_tokens(text: str) -> int:
    """
    Approximate token count using simple whitespace splitting.
    This is a rough approximation - for exact counts, use tiktoken or transformers.

    Approximation: ~1.3 tokens per word (common for English with GPT tokenizers)
    """
    words = len(text.split())
    return int(words * 1.3)


def split_text_strict(text: str, max_tokens: int) -> List[str]:
    """
    Split text into chunks of approximately max_tokens size.
    Strict mode: Splits at exact token boundaries, may break mid-sentence.

    Args:
        text: Text to split
        max_tokens: Maximum tokens per chunk

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    # Approximate: max_tokens / 1.3 = max words
    max_words = int(max_tokens / 1.3)

    for word in words:
        word_tokens = 1.3  # Approximately 1.3 tokens per word

        if current_tokens + word_tokens > max_tokens and current_chunk:
            # Save current chunk and start new one
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    # Add remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def split_text_paragraph_aware(text: str, max_tokens: int) -> List[str]:
    """
    Split text into chunks respecting paragraph boundaries.
    Tries to keep paragraphs together when possible.

    Args:
        text: Text to split (should have \\n\\n for paragraph breaks)
        max_tokens: Maximum tokens per chunk

    Returns:
        List of text chunks
    """
    # Split into paragraphs (double newline)
    paragraphs = patterns.PARAGRAPH_SPLIT.split(text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = count_tokens(para)

        # If single paragraph exceeds max_tokens, split it strictly
        if para_tokens > max_tokens:
            # Finish current chunk first
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0

            # Split the large paragraph
            para_chunks = split_text_strict(para, max_tokens)
            chunks.extend(para_chunks)

        # If adding this paragraph would exceed limit, start new chunk
        elif current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens

        # Otherwise add to current chunk
        else:
            current_chunk.append(para)
            current_tokens += para_tokens

    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def split_text(text: str, max_tokens: int, strict: bool = False) -> List[str]:
    """
    Split text into chunks of approximately max_tokens size.

    Args:
        text: Text to split
        max_tokens: Maximum tokens per chunk
        strict: If True, split at exact boundaries. If False, respect paragraphs.

    Returns:
        List of text chunks
    """
    if strict:
        return split_text_strict(text, max_tokens)
    else:
        return split_text_paragraph_aware(text, max_tokens)


def text_to_jsonl_records(
    text: str,
    max_tokens: int,
    strict: bool = False,
    source_file: str = None,
    metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Convert text to JSONL records with token-based chunking.

    Args:
        text: Text to convert
        max_tokens: Maximum tokens per chunk
        strict: Whether to split strictly or respect paragraphs
        source_file: Source filename (for metadata)
        metadata: Additional metadata to include in each record

    Returns:
        List of dictionaries ready for JSONL serialization
    """
    chunks = split_text(text, max_tokens, strict=strict)

    records = []
    for i, chunk in enumerate(chunks):
        record = {
            'text': chunk,
            'chunk_index': i,
            'total_chunks': len(chunks),
            'token_count': count_tokens(chunk),
        }

        if source_file:
            record['source_file'] = source_file

        if metadata:
            record.update(metadata)

        records.append(record)

    return records
