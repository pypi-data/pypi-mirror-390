"""PDF text extraction using external tools."""

import subprocess
import time


def extract_pdf_text(pdf_path, output_path):
    """
    Extract text from PDF using pdftotext (poppler-utils).

    Falls back to raw mode if layout mode fails.

    Returns:
        Tuple of (success: bool, duration: float, method: str)
    """
    # Try layout mode first (preserves formatting)
    try:
        start = time.time()
        subprocess.run(
            f'pdftotext -layout "{pdf_path}" "{output_path}"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, time.time() - start, "pdftotext-layout"
    except subprocess.CalledProcessError:
        pass

    # Fallback to raw mode (no layout)
    try:
        start = time.time()
        subprocess.run(
            f'pdftotext -raw "{pdf_path}" "{output_path}"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, time.time() - start, "pdftotext-raw"
    except subprocess.CalledProcessError:
        return False, 0, None
