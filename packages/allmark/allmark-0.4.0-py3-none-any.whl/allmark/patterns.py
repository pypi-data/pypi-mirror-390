"""Regex patterns for text cleaning and detection.

This module centralizes all regex patterns used throughout allmark,
making it easy to add new patterns or customize existing ones.

All patterns are organized by category and follow a consistent naming convention:
- Pattern names are UPPERCASE with underscores
- Related patterns are grouped together
- Each section has a clear header comment
"""

import re

# ============================================================================
# UNICODE CHARACTER PATTERNS
# ============================================================================

# Unicode normalization patterns
UNICODE_DASHES = re.compile(r'[‐-‒–—―﹘]+')  # Any dash-like character
UNICODE_APOSTROPHES = re.compile(r"[''‛′ʹ]")  # Any apostrophe variant
UNICODE_QUOTES = re.compile(r"[""‟″]")        # Any quote variant
SUPERSCRIPTS = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]")    # Superscript numbers
FRACTIONS = re.compile(r"[¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]")  # Unicode fractions

# Whitespace variants
ZERO_WIDTH = re.compile(r'[\u200B\u200C\u200D\uFEFF]')  # Zero-width chars
NBSP = re.compile(r'\u00A0')  # Non-breaking space

# ============================================================================
# OCR ARTIFACT PATTERNS
# ============================================================================

# Soft hyphens
SOFT_HYPHEN = re.compile(r'\u00AD')  # Unicode soft hyphen
SOFT_HYPHEN_SPACE = re.compile(r'(\w)¬\s*(\w)')  # Soft hyphen with space

# Broken hyphenation patterns (from Marker project)
# Matches: lowercase/digit + hyphen + optional space + newline + lowercase/digit
BROKEN_HYPHENATION = re.compile(
    r'([a-z0-9])[-–—¬]\s?\n\s*([a-z0-9])',
    re.IGNORECASE
)

# Ligature replacements - common OCR artifacts
LIGATURES = {
    # Common ligatures
    'ﬁ': 'fi',
    'ﬂ': 'fl',
    'ﬀ': 'ff',
    'ﬃ': 'ffi',
    'ﬄ': 'ffl',
    'ﬆ': 'st',
    'ﬅ': 'ft',
    # Rare ligatures (old scans)
    '﬊': 'fj',
    '﬋': 'ffj',
    # Medieval ligatures
    'ꜳ': 'aa',
    'ꜵ': 'ao',
    'ꜷ': 'av',
    'ꜹ': 'ay',
    'ꜻ': 'ee',
    'ꜽ': 'oe',
    'ꜿ': 'oo',
    'ﬓ': 'mn',
    'ﬔ': 'me',
    'ﬕ': 'mi',
    'ﬖ': 'vu',
}

# Ellipsis patterns
ELLIPSIS = re.compile(
    r'(…|'                      # Unicode ellipsis
    r'\s*\.\s*\.\s*\.\s*|'      # Spaced or unspaced 3 dots
    r'\s*·\s*·\s*·\s*|'         # Bullet ellipsis
    r'(?:\.\s*){3,})'           # 4 or more dots
)

# Control characters (except newlines and tabs)
CONTROL_CHARS = re.compile(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]')

# ============================================================================
# EBOOK ARTIFACT PATTERNS
# ============================================================================

# Markdown image and link patterns
IMAGE_MARKDOWN = re.compile(r'!\[.*?\]\(.*?\)')
LINK_MARKDOWN = re.compile(r'\[.*?\]\([^\)]+\)')
URL_PATTERN = re.compile(r'http[s]?://[^\s\)]+')

# Pandoc/ePub metadata markers
CLASS_MARKER = re.compile(r'\{\.[\w\-]+\}')
CLASS_BRACKET = re.compile(r'\[([^\]]+)\]\{\.[\w\-]+\}')
ID_MARKER = re.compile(r'\{#[\w\-]+\}')
STYLE_ATTR = re.compile(r'\{style="[^"]*"\}')
HEIGHT_ATTR = re.compile(r'\{height="[^"]*"[^\}]*\}')
WIDTH_ATTR = re.compile(r'\{width="[^"]*"[^\}]*\}')
CLASS_ATTR = re.compile(r'\{class="[^"]*"[^\}]*\}')

# Standalone markers on their own lines
STANDALONE_CLASS = re.compile(r'^\s*\{\.[\w\-]+\}\s*$', re.MULTILINE)
STANDALONE_BRACKET = re.compile(r'^\s*\[\]\{[^\}]+\}\s*$', re.MULTILINE)

# Pandoc/ePub format artifacts
PANDOC_HTML = re.compile(r'`+\{=html\}`+')
EPUB_HTML = re.compile(r'\{=html\}')
EPUB_TYPE = re.compile(r'epub:type="[^"]*"')

# Calibre ebook manager artifacts
CALIBRE_ID = re.compile(r'\bcalibre\d+\b')
CALIBRE_CLASS = re.compile(r'\.calibre\d+')

# Div/span markers from conversion
DIV_MARKER = re.compile(r'::+\s*\{[^\}]*\}')
STANDALONE_DIV = re.compile(r'^::+\s*\w*\s*$', re.MULTILINE)

# Copyright and legal text artifacts
COPY_PREFIX = re.compile(r'^\s*copy\d*\s+', re.MULTILINE)
COPYRIGHT_YEAR = re.compile(r'copyright\s+\d{4}', re.IGNORECASE)

# HTML tags
HTML_TAG = re.compile(r'<[^>]+>')

# Bracket and parenthesis cleanup
EMPTY_BRACKETS = re.compile(r'\[\s*\]')
EMPTY_PARENS = re.compile(r'\(\s*\)')
SPLIT_CAPITALS = re.compile(r'([A-Z])\[([A-Z]+)\]')  # "F[OR A MAN]" -> "FOR A MAN"
REMAINING_BRACKETS = re.compile(r'\[([^\]]*)\]')     # All remaining brackets

# Short bracket text to emphasis conversion (unused - kept for potential use)
BRACKET_EMPHASIS_SPACE = re.compile(r'(\s)\[([^\]]{1,50}?)\](\s)')
BRACKET_EMPHASIS_PUNCT = re.compile(r'(\s)\[([^\]]{1,50}?)\]([.,;:!?\)])')
BRACKET_EMPHASIS_START = re.compile(r'(^|\n)\[([^\]]{1,50}?)\](\s)')

# ============================================================================
# PAGE NUMBER PATTERNS
# ============================================================================

PAGE_NUMBER_PATTERNS = [
    # Simple standalone numbers (1-999)
    re.compile(r'^\s*\d{1,3}\s*$'),

    # Numbers with dashes: "- 42 -" or "-42-"
    re.compile(r'^\s*-\s*\d+\s*-\s*$'),
    re.compile(r'^\s*-\d+-\s*$'),

    # Numbers with dots/periods: ". 42 ." or ".42."
    re.compile(r'^\s*\.\s*\d+\s*\.\s*$'),
    re.compile(r'^\s*\.\d+\.\s*$'),

    # Numbers with brackets: "[42]" or "[[42]]"
    re.compile(r'^\s*\[+\s*\d+\s*\]+\s*$'),

    # Numbers with pipes: "| 42 |"
    re.compile(r'^\s*\|\s*\d+\s*\|\s*$'),

    # Numbers with underscores: "_42_" or "__42__"
    re.compile(r'^\s*_+\s*\d+\s*_+\s*$'),

    # "Page N" or "Page 42"
    re.compile(r'^\s*Page\s+\d+\s*$', re.IGNORECASE),

    # Numbers with HTML/markup artifacts
    re.compile(r'^\s*<\w+>\s*\d+\s*</\w+>\s*$'),
    re.compile(r'^\s*\{[^\}]*\}\s*\d+\s*$'),
    re.compile(r'^\s*\d+\s*\{[^\}]*\}\s*$'),

    # Numbers with extra spacing/formatting
    re.compile(r'^\s+\d{1,3}\s+$'),

    # Roman numeral page numbers (i, ii, iii, iv, v, etc.)
    re.compile(r'^\s*[ivxlc]{1,6}\s*$', re.IGNORECASE),
]

# ============================================================================
# TABLE OF CONTENTS (TOC) PATTERNS
# ============================================================================

# TOC line endings with page numbers
TOC_PAGE_NUMBER = re.compile(r'\b\d{1,4}\s*$')
TOC_DOTTED_LEADERS = re.compile(r'\.{2,}\s*\d{1,4}\s*$')
TOC_ROMAN_CHAPTER = re.compile(r'^\s*[IVX]{1,6}\.\s+\w')

# ============================================================================
# HEADER/FOOTER PATTERNS
# ============================================================================

# Header patterns for detect_repeating_headers_footers
HEADER_PAGE_NUMBER = re.compile(r'^\s*\d{1,4}\s*$')

# ============================================================================
# INDEX SECTION PATTERNS
# ============================================================================

# Index section header pattern
INDEX_HEADER = re.compile(r'^\s*#{0,3}\s*Index\s*$', re.IGNORECASE)

# ============================================================================
# CHAPTER DETECTION PATTERNS
# ============================================================================

# Chapter patterns for finding first chapter (conservative)
CHAPTER_PATTERNS = [
    # Parts and Acts
    re.compile(r'^\s*#{0,3}\s*(Part\s+(One|Two|Three|Four|Five|1|2|3|4|5|I|II|III|IV|V))\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*(Act\s+(One|Two|Three|Four|Five|1|2|3|4|5|I|II|III|IV|V))\s*$', re.IGNORECASE),

    # Specific chapter openings
    re.compile(r'^\s*#{0,3}\s*(Chapter\s+(One|Two|Three|1|2|3|I|II|III))\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*Chapter\s+1\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*Chapter\s+One\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*Chapter\s+I\s*$', re.IGNORECASE),

    # Bracketed chapter numbers: "[[1]]" or "[1]"
    re.compile(r'^\s*\[\[?\s*(\d+)\s*\]?\]\s*$'),

    # Roman numerals alone
    re.compile(r'^\s*([IVX]{1,6})\s*$'),

    # First part/act patterns
    re.compile(r'^\s*Part\s+(One|1|I)\s*$', re.IGNORECASE),
    re.compile(r'^\s*Act\s+(One|1|I)\s*$', re.IGNORECASE),
]

# All chapter markers (more permissive - for finding all chapters)
ALL_CHAPTER_PATTERNS = [
    re.compile(r'^\s*#{0,3}\s*Chapter\s+(\d+|[IVXivx]+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*Part\s+(\d+|[IVXivx]+|One|Two|Three|Four|Five)\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*Act\s+(\d+|[IVXivx]+|One|Two|Three|Four|Five)\s*$', re.IGNORECASE),
    re.compile(r'^\s*\[\[?\s*(\d+)\s*\]?\]\s*$'),  # [[1]] or [1]
    re.compile(r'^\s*([IVX]{1,6})\s*$'),           # Roman numerals alone
]

# Chapter standardization patterns
CHAPTER_BRACKET = re.compile(r'^\[\[?\s*(\d+)\s*\]?\]$')
CHAPTER_WORD = re.compile(r'^(Chapter|CHAPTER|Ch\.?)\s+(\d+|[IVXivx]+)\s*$', re.IGNORECASE)
CHAPTER_NUMBER = re.compile(r'^(\d+)$')
CHAPTER_ROMAN = re.compile(r'^([IVX]{1,6})$')

# ============================================================================
# FRONTMATTER/BACKMATTER KEYWORDS
# ============================================================================

FRONTMATTER_KEYWORDS = [
    # Legal/copyright
    'copyright', '©', 'isbn', 'published by', 'first published',
    'all rights reserved', 'library of congress', 'cataloging',
    'printing', 'edition', 'permissions', 'rights@', 'publisher',

    # Digital format markers
    'e-book', 'ebook', 'author and publisher', 'personal use',

    # Contact/web
    'email', 'http', 'www',

    # Other books
    'also by', 'books by', 'other works', 'fiction by',

    # Reviews/praise
    'praise for', 'acclaim for', 'reviews', 'advance praise',

    # Structure
    'table of contents', 'contents',

    # Credits
    'dedication', 'acknowledgments', 'acknowledgements',
    'foreword', 'preface', 'introduction by',
    'translated by', 'edited by',

    # Book parts
    'title page', 'half title', 'frontispiece',
]

BACKMATTER_KEYWORDS = [
    # Credits/acknowledgments
    'acknowledgment', 'acknowledgement',

    # Author info
    'about the author', 'author bio', 'biography',
    'a note on',

    # Other books
    'also by', 'other books', 'coming soon',
    'next in the series',

    # Previews/excerpts
    'preview', 'preview of', 'excerpt from',
    'teaser', 'sneak peek',

    # Discussion guides
    'discussion questions', 'reading group',
    'reading group guide', 'book club',

    # Academic
    'notes', 'endnotes', 'bibliography', 'works cited',
    'glossary', 'index', 'appendix',

    # Endings
    'afterword', 'epilogue', 'colophon',

    # Publisher
    'about the publisher',
]

BACKMATTER_PATTERNS = [
    re.compile(r'^\s*#{0,3}\s*(Acknowledgments?|Acknowledgements?)\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*About the Author\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*(Also [Bb]y|Other [Bb]ooks)\s*$'),
    re.compile(r'^\s*#{0,3}\s*(Notes?|Endnotes?|Bibliography)\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*(Copyright|Colophon)\s*$', re.IGNORECASE),
    re.compile(r'^\s*A Note on the Author\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*(Preview|Excerpt)\s*$', re.IGNORECASE),
    re.compile(r'^\s*#{0,3}\s*Discussion Questions\s*$', re.IGNORECASE),
]

# End of book markers
END_MARKERS = ['the end', 'end', 'fin', 'finis']

# ============================================================================
# JUNK DETECTION PATTERNS
# ============================================================================

JUNK_PATTERNS = [
    re.compile(r'[■�◆□◼◻◾◽●○◊◇¤^~_=]{2,}'),  # Symbol sequences
    re.compile(r'[|]{3,}'),                        # Multiple pipes
    re.compile(r'[•]{3,}'),                        # Multiple bullets
    re.compile(r'[=]{3,}'),                        # Multiple equals
    re.compile(r'^[\s\W]{5,}$'),                   # Only punctuation/symbols
    re.compile(r'^\s*[il\|]{10,}\s*$'),           # Columns of pipes/l/i
    re.compile(r'\bhttp[s]?://'),                  # URLs
    re.compile(r'\bwww\.'),                        # www URLs
    re.compile(r'\bISBN\b'),                       # ISBN
    re.compile(r'[{}<>;]{2,}'),                    # Code-like brackets
]

# ============================================================================
# CODE DETECTION PATTERNS
# ============================================================================

# Pattern list: (regex, weight)
CODE_PATTERNS = [
    # Keywords
    (re.compile(r'^(import|from|def|class|function|var|let|const|public|private)\s', re.IGNORECASE), 3),

    # Constants: CONSTANT = value
    (re.compile(r'^[A-Z_][A-Z0-9_]*\s*='), 2),

    # Multiple brace pairs
    (re.compile(r'\{[^}]+\}.*\{[^}]+\}'), 2),

    # HTML/XML tags
    (re.compile(r'<[a-z]+[^>]*>'), 2),

    # Control structures
    (re.compile(r'^\s*(if|for|while|switch|try|catch)\s*\(', re.IGNORECASE), 3),

    # Operators: =>, ->, ||, &&, ==, !=, <=, >=
    (re.compile(r'=>|->|\|\||&&|==|!=|<=|>='), 2),

    # Ends with semicolon
    (re.compile(r';$'), 1),

    # Comments: //, /*, */
    (re.compile(r'^\s*//|^\s*/\*|^\s*\*/'), 2),

    # Array literals: [1, 2, 3]
    (re.compile(r'\[[\d\s,]+\]'), 1),

    # Template literals: ${var}
    (re.compile(r'\$\{[^}]+\}'), 2),

    # Function definitions
    (re.compile(r'^[a-z_][a-z0-9_]*\s*\(.*\)\s*[{:]'), 3),
]

# ============================================================================
# MARKDOWN FORMATTING PATTERNS
# ============================================================================

# Headers with missing space: "#Chapter" -> "# Chapter"
HEADER_NO_SPACE = re.compile(r'^(#{1,6})([^#\s])')

# Emphasis with spaces: "* text *" -> "*text*"
EMPHASIS_STAR_SPACE = re.compile(r'\*\s+([^*]+?)\s+\*')
EMPHASIS_UNDER_SPACE = re.compile(r'_\s+([^_]+?)\s+_')

# Multiple emphasis markers
MULTIPLE_STARS = re.compile(r'\*{3,}')
MULTIPLE_UNDERS = re.compile(r'_{3,}')

# Header spacing
HEADER_BEFORE = re.compile(r'\n(#{1,6}\s)')
HEADER_AFTER = re.compile(r'(#{1,6}\s[^\n]+)\n([^\n#])')

# Excessive whitespace
EXCESSIVE_NEWLINES = re.compile(r'\n{4,}')
TRAILING_WHITESPACE = re.compile(r'[ \t]+$', re.MULTILINE)

# Artifact-only lines (brackets, parens, punctuation, etc.)
ARTIFACT_LINE = re.compile(r'^[\[\](){}\s\*\-_.:;]+$')

# Standalone title markers: "_TITLE_"
TITLE_MARKER = re.compile(r'^_[A-Z\s]+_\n+')

# ============================================================================
# TEXT ANALYSIS PATTERNS
# ============================================================================

# Terminal punctuation with optional quote/paren/bracket closure
TERMINAL_PUNCTUATION = re.compile(r'[.!?…]+["\'\)\]»"\']*$')

# Citation and footnote patterns (used in helper functions)
FOOTNOTE_MARKER = re.compile(r'^\[\s*[\d\*†‡§¶#a-z]\s*\]$')
CITATION_PATTERN = re.compile(r'\[[\w\s]+\s+\d{4}\]')

# Table detection patterns
TABLE_COLUMN_SPACING = re.compile(r'  {3,}')  # 3+ consecutive spaces
TABLE_COLUMN_SPLIT = re.compile(r'  {2,}')   # 2+ spaces for splitting

# Index entry patterns
INDEX_ENTRY_SINGLE_PAGE = re.compile(r',\s*\d+(\s*[-–]\s*\d+)?\s*$')
INDEX_ENTRY_MULTI_PAGE = re.compile(r',\s*\d+(\s*,\s*\d+){2,}\s*$')

# Paragraph splitting pattern
PARAGRAPH_SPLIT = re.compile(r'\n\n+')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_page_number(line: str) -> bool:
    """
    Check if a line matches any page number pattern.

    Args:
        line: Line of text to check

    Returns:
        True if line appears to be a page number
    """
    stripped = line.strip()
    return any(pattern.match(stripped) for pattern in PAGE_NUMBER_PATTERNS)


def is_junk(line: str) -> bool:
    """
    Check if a line matches any junk pattern.

    Junk includes symbol sequences, URL fragments, ISBN numbers,
    and lines with low alphanumeric content ratio.

    Args:
        line: Line of text to check

    Returns:
        True if line appears to be junk/artifacts
    """
    stripped = line.strip()
    if not stripped:
        return False

    # Check alphanumeric ratio (must be at least 55% alphanumeric)
    alnum = sum(c.isalnum() for c in stripped)
    if alnum / max(1, len(stripped)) < 0.55:
        return True

    return any(pattern.search(stripped) for pattern in JUNK_PATTERNS)


def is_code_like(line: str, threshold: int = 3) -> bool:
    """
    Check if a line looks like code (score >= threshold).

    Uses weighted pattern matching and structural analysis to detect
    programming code vs. prose.

    Args:
        line: Line of text to check
        threshold: Minimum score to consider as code (default: 3)

    Returns:
        True if line appears to be code
    """
    stripped = line.strip()
    if not stripped:
        return False

    score = 0

    # Check patterns with weights
    for pattern, weight in CODE_PATTERNS:
        if pattern.search(stripped):
            score += weight

    # Structural indicators
    if stripped.count('{') + stripped.count('}') >= 2:
        score += 1
    if stripped.count('(') + stripped.count(')') >= 3:
        score += 1
    if stripped.count('[') + stripped.count(']') >= 2:
        score += 1

    # High ratio of special chars to letters
    special = sum(1 for c in stripped if c in '{}[]()<>=;:,.|&*%$#@!+-/')
    if len(stripped) > 0 and special / len(stripped) > 0.3:
        score += 2

    return score >= threshold


def matches_chapter_pattern(line: str) -> bool:
    """
    Check if line matches any chapter pattern (conservative).

    Used for finding the first chapter in frontmatter detection.

    Args:
        line: Line of text to check

    Returns:
        True if line appears to be a chapter marker
    """
    stripped = line.strip()
    return any(pattern.match(stripped) for pattern in CHAPTER_PATTERNS)


def matches_all_chapter_pattern(line: str) -> bool:
    """
    Check if line matches any chapter pattern (permissive).

    Used for finding all chapters throughout the document.

    Args:
        line: Line of text to check

    Returns:
        True if line appears to be a chapter marker
    """
    stripped = line.strip()
    return any(pattern.match(stripped) for pattern in ALL_CHAPTER_PATTERNS)


def has_terminal_punctuation(line: str) -> bool:
    """
    Check if line ends with terminal punctuation.

    Terminal punctuation includes: . ! ? ... …
    Also handles quote/paren/bracket closure after punctuation.

    Args:
        line: Line of text to check

    Returns:
        True if line ends with terminal punctuation
    """
    stripped = line.rstrip()
    if not stripped:
        return False

    # Terminal punctuation with optional quote/paren/bracket closure
    # Matches: . ! ? ... … followed by optional " ' ) ] » "
    return bool(TERMINAL_PUNCTUATION.search(stripped))


def is_dialogue_line(line: str, prev_line: str = None) -> bool:
    """
    Check if line appears to be dialogue.

    Detects:
    - Lines starting with quote marks
    - Lines starting with em-dash
    - Lines following dialogue tags (he said, she said, etc.)

    Args:
        line: Line of text to check
        prev_line: Previous line for context (optional)

    Returns:
        True if line appears to be dialogue
    """
    stripped = line.lstrip()
    if not stripped:
        return False

    # Starts with quote marks (various Unicode variants)
    if stripped[0] in '"\'""\u2018\u201c\u2039\u00ab':
        return True

    # Starts with em-dash (dialogue without quotes)
    if stripped.startswith('—') or stripped.startswith('--'):
        return True

    # Previous line ends with dialogue tag
    if prev_line:
        prev_lower = prev_line.lower().rstrip()
        dialogue_tags = [
            'he said', 'she said', 'they said', 'said',
            'asked', 'replied', 'whispered', 'shouted',
            'exclaimed', 'muttered', 'answered'
        ]
        if any(prev_lower.endswith(tag + '.') or prev_lower.endswith(tag + ',') for tag in dialogue_tags):
            return True

    return False


def detect_poetry_section(lines: list, start_idx: int, min_lines: int = 4) -> int:
    """
    Detect if a poetry/verse section starts at start_idx.

    Poetry heuristics:
    - Short lines (< 60 chars) clustered together
    - Consistent indentation patterns
    - Stanza breaks (empty lines between groups)

    Args:
        lines: List of text lines
        start_idx: Starting index to check
        min_lines: Minimum lines to qualify as poetry (default: 4)

    Returns:
        Number of consecutive poetry lines (0 if not poetry)
    """
    if start_idx >= len(lines):
        return 0

    poetry_count = 0
    short_line_count = 0
    i = start_idx

    while i < len(lines) and i < start_idx + 50:  # Max 50 line lookahead
        line = lines[i].rstrip()

        # Empty line in poetry (stanza break)
        if not line:
            if short_line_count >= min_lines:
                poetry_count += 1
                i += 1
                continue
            else:
                break

        # Long line breaks poetry
        if len(line) > 80:
            break

        # Short line
        if len(line) < 60:
            short_line_count += 1
            poetry_count += 1
        else:
            # Allow occasional longer lines in poetry
            if short_line_count >= min_lines:
                poetry_count += 1
            else:
                break

        i += 1

    # Need minimum lines to qualify as poetry
    return poetry_count if short_line_count >= min_lines else 0


def is_citation_or_footnote(text: str) -> bool:
    """
    Check if bracketed text is likely a citation or footnote.

    Detects:
    - Footnote markers: [1], [*], [†], [a]
    - Citations: [Author YEAR], [Smith 2020]
    - Editorial markers: [sic], [emphasis added], [...]

    Args:
        text: Bracketed text to check

    Returns:
        True if text appears to be a citation or footnote
    """
    # Footnote markers: [1], [*], [†], [a]
    if FOOTNOTE_MARKER.match(text):
        return True

    # Citations: [Author YEAR], [Smith 2020], [Jones et al. 2019]
    if CITATION_PATTERN.search(text):
        return True

    # Editorial markers: [sic], [emphasis added], [...]
    editorial = [
        'sic', 'emphasis added', 'emphasis mine',
        '...', 'ellipsis', 'note', 'editor', 'translator'
    ]
    if any(f'[{marker}]' in text.lower() for marker in editorial):
        return True

    return False


def is_table_row(line: str) -> bool:
    """
    Check if line looks like a table row.

    Detects:
    - Markdown table syntax (pipes)
    - Tab-separated values
    - Multiple spaces (aligned columns)

    Args:
        line: Line of text to check

    Returns:
        True if line appears to be a table row
    """
    stripped = line.strip()
    if not stripped:
        return False

    # Markdown table syntax
    if '|' in stripped and stripped.count('|') >= 2:
        return True

    # Tab-separated values
    if '\t' in stripped and stripped.count('\t') >= 2:
        return True

    # Multiple spaces (aligned columns) - 3+ consecutive spaces
    if TABLE_COLUMN_SPACING.search(stripped):
        parts = TABLE_COLUMN_SPLIT.split(stripped)
        if len(parts) >= 3:  # At least 3 columns
            return True

    return False


def is_index_entry(line: str) -> bool:
    """
    Check if line looks like an index entry.

    Index entries typically follow patterns like:
    - "Term, 42"
    - "Term, 42-45"
    - "Term, 42, 68, 120"
    - "  Subterm, 50" (indented)

    Args:
        line: Line of text to check

    Returns:
        True if line appears to be an index entry
    """
    stripped = line.strip()
    if not stripped:
        return False

    # Ends with page number(s): "Term, 42" or "Term, 42-45"
    if INDEX_ENTRY_SINGLE_PAGE.search(stripped):
        return True

    # Multiple page numbers: "term, 10, 20, 30"
    if INDEX_ENTRY_MULTI_PAGE.search(stripped):
        return True

    return False
