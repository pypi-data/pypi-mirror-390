"""PDF text extraction using external tools with multiple strategies."""

import subprocess
import time
import os

from . import patterns


def _analyze_text_quality(text):
    """
    Analyze extracted text quality to determine best extraction method.

    Returns a quality score (higher is better).
    """
    if not text or len(text) < 50:
        return 0

    score = 0

    # Penalize corrupted characters
    corrupted_chars = len(patterns.CORRUPTED_CHARS.findall(text))
    score -= corrupted_chars * 10

    # Penalize excessive special characters that indicate OCR errors
    special_chars = len(patterns.EXCESSIVE_SPECIAL_CHARS.findall(text))
    score -= (special_chars / len(text)) * 100

    # Reward proper word spacing
    words = text.split()
    avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
    if 3 <= avg_word_len <= 8:  # Normal English word length
        score += 50

    # Reward proper line breaks and paragraphs
    lines = text.split('\n')
    if len(lines) > 1:
        score += min(len(lines) / 10, 50)

    # Penalize excessive whitespace
    whitespace_ratio = (len(text) - len(text.replace(' ', ''))) / len(text)
    if whitespace_ratio > 0.3:
        score -= (whitespace_ratio - 0.3) * 200

    return score


def _extract_with_pdftotext_layout(pdf_path, output_path):
    """Extract using pdftotext -layout (best for formatted text)."""
    try:
        start = time.time()
        subprocess.run(
            f'pdftotext -layout "{pdf_path}" "{output_path}"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return True, time.time() - start, "pdftotext-layout", text
    except (subprocess.CalledProcessError, IOError):
        pass
    return False, 0, None, ""


def _extract_with_pdftotext_raw(pdf_path, output_path):
    """Extract using pdftotext -raw (for simple text extraction)."""
    try:
        start = time.time()
        subprocess.run(
            f'pdftotext -raw "{pdf_path}" "{output_path}"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return True, time.time() - start, "pdftotext-raw", text
    except (subprocess.CalledProcessError, IOError):
        pass
    return False, 0, None, ""


def _extract_with_pdftotext_nopgbrk(pdf_path, output_path):
    """Extract using pdftotext -nopgbrk (removes page breaks)."""
    try:
        start = time.time()
        subprocess.run(
            f'pdftotext -nopgbrk "{pdf_path}" "{output_path}"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return True, time.time() - start, "pdftotext-nopgbrk", text
    except (subprocess.CalledProcessError, IOError):
        pass
    return False, 0, None, ""


def _extract_with_pdftotext_enc_utf8(pdf_path, output_path):
    """Extract using pdftotext with explicit UTF-8 encoding."""
    try:
        start = time.time()
        subprocess.run(
            f'pdftotext -enc UTF-8 -layout "{pdf_path}" "{output_path}"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return True, time.time() - start, "pdftotext-utf8", text
    except (subprocess.CalledProcessError, IOError):
        pass
    return False, 0, None, ""


def extract_pdf_text(pdf_path, output_path):
    """
    Extract text from PDF using multiple strategies and select the best result.

    Tries multiple extraction methods and selects the one with highest quality score.

    Returns:
        Tuple of (success: bool, duration: float, method: str)
    """
    extraction_methods = [
        _extract_with_pdftotext_enc_utf8,  # Try UTF-8 encoding first for character issues
        _extract_with_pdftotext_layout,     # Then layout mode
        _extract_with_pdftotext_nopgbrk,    # Then no page breaks
        _extract_with_pdftotext_raw,        # Finally raw mode
    ]

    results = []
    total_start = time.time()

    for method in extraction_methods:
        # Use temporary file for each method
        temp_output = output_path + ".tmp"
        success, duration, method_name, text = method(pdf_path, temp_output)

        if success and text:
            quality = _analyze_text_quality(text)
            results.append((quality, duration, method_name, text, temp_output))

        # Clean up temp file
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
            except:
                pass

    if not results:
        return False, 0, None

    # Select the best result based on quality score
    results.sort(key=lambda x: x[0], reverse=True)
    best_quality, best_duration, best_method, best_text, _ = results[0]

    # Write the best result to the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(best_text)
    except IOError:
        return False, 0, None

    total_duration = time.time() - total_start
    return True, total_duration, best_method
