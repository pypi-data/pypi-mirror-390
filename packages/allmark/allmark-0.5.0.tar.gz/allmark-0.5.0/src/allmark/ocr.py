"""OCR artifact repair utilities."""

from . import patterns


def repair_ocr_artifacts(text):
    """Repair common OCR artifacts and broken hyphenation."""
    # Fix soft hyphens
    text = text.replace('\u00AD', '')

    # Fix broken hyphenation across lines with enhanced pattern
    # Handles: regular hyphen (-), em-dash (—), en-dash (–), and special hyphen (¬)
    # Pattern from Marker: matches lowercase/digit + hyphen + optional space + newline + lowercase/digit
    text = patterns.BROKEN_HYPHENATION.sub(r'\1\2\n', text)

    # Fix soft hyphen with space: "conven¬ tional" -> "conventional"
    text = patterns.SOFT_HYPHEN_SPACE.sub(r'\1\2', text)

    # Fix ligature issues (common OCR problems)
    for lig, rep in patterns.LIGATURES.items():
        text = text.replace(lig, rep)

    # Normalize ellipses: ". . ." or "· · ·" -> "..."
    text = patterns.ELLIPSIS.sub('...', text)

    # Remove control characters (except newlines and tabs)
    text = patterns.CONTROL_CHARS.sub('', text)

    # Remove BOM and private use characters
    text = text.replace('\ufeff', '').replace('\ue000', '').replace('\ue001', '').replace('\ue002', '')

    return text
