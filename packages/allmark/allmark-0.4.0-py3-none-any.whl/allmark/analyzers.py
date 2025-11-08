"""Document analysis utilities."""

import statistics
from . import patterns


def analyze_document_structure(text):
    """Analyze document to understand its characteristics and build confidence scores."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    if not lines:
        return {}

    analysis = {
        'total_lines': len(lines),
        'line_lengths': [len(l) for l in lines],
        'avg_line_length': statistics.mean([len(l) for l in lines]),
        'median_line_length': statistics.median([len(l) for l in lines]),
        'prose_lines': [],
        'short_lines': [],
        'code_like_lines': [],
        'uppercase_lines': [],
        'url_lines': [],
        'has_chapters': False,
        'chapter_positions': [],
    }

    # Calculate std dev for line lengths
    if len(lines) > 1:
        analysis['line_length_stdev'] = statistics.stdev([len(l) for l in lines])
    else:
        analysis['line_length_stdev'] = 0

    # Analyze each line
    for i, line in enumerate(lines):
        length = len(line)

        # Prose characteristics
        if length > 100 and line[0].isupper() and '.' in line:
            words = line.split()
            if len(words) >= 10:
                analysis['prose_lines'].append(i)

        # Short lines (potential metadata, headers, artifacts)
        if length < 40:
            analysis['short_lines'].append(i)

        # Code-like patterns
        if any(pattern in line for pattern in ['{', '}', '<', '>', '=', ';', '//', '/*', '*/']):
            if line.count('{') + line.count('}') >= 2 or line.count('<') + line.count('>') >= 2:
                analysis['code_like_lines'].append(i)

        # ALL CAPS (potential running headers)
        if length > 10 and line.isupper() and line.isalpha():
            analysis['uppercase_lines'].append(i)

        # URLs and technical content
        if 'http://' in line.lower() or 'www.' in line.lower() or '@' in line:
            analysis['url_lines'].append(i)

    # Calculate prose density (what % of doc is sustained prose)
    analysis['prose_density'] = len(analysis['prose_lines']) / max(1, len(lines))

    # Detect narrative sections (3+ consecutive prose lines)
    narrative_sections = []
    current_section = []
    for i in range(len(lines)):
        if i in analysis['prose_lines']:
            current_section.append(i)
        else:
            if len(current_section) >= 3:
                narrative_sections.append((current_section[0], current_section[-1]))
            current_section = []
    if len(current_section) >= 3:
        narrative_sections.append((current_section[0], current_section[-1]))

    analysis['narrative_sections'] = narrative_sections
    analysis['has_sustained_narrative'] = len(narrative_sections) > 0

    return analysis


def score_frontmatter_confidence(lines, idx, analysis):
    """Score how confident we are that idx is in frontmatter (0-1 scale)."""
    if idx >= len(lines):
        return 0.0

    score = 0.0
    line = lines[idx].strip().lower()

    # Strong frontmatter indicators (high weight)
    strong_indicators = [
        'copyright', '©', 'isbn', 'published by', 'first published',
        'all rights reserved', 'library of congress', 'cataloging',
        'printing', 'edition', 'permissions', 'rights@', 'publisher',
        'acknowledgments', 'acknowledgements', 'dedication',
        'table of contents', 'contents', 'foreword', 'preface',
        'introduction by', 'translated by', 'edited by',
        'praise for', 'acclaim for', 'reviews', 'advance praise',
        'also by', 'books by', 'other works', 'fiction by',
        'title page', 'half title', 'frontispiece'
    ]

    if any(kw in line for kw in strong_indicators):
        score += 0.5

    # Position-based scoring (first 10% more likely frontmatter)
    if idx < len(lines) * 0.1:
        score += 0.2

    # Before any narrative section
    if analysis.get('narrative_sections'):
        first_narrative = analysis['narrative_sections'][0][0]
        if idx < first_narrative:
            score += 0.2

    # Very short line with capitalized words (often metadata)
    if len(lines[idx]) < 50 and sum(1 for c in lines[idx] if c.isupper()) > 3:
        score += 0.1

    return min(1.0, score)


def score_backmatter_confidence(lines, idx, analysis):
    """Score how confident we are that idx is in backmatter (0-1 scale)."""
    if idx >= len(lines):
        return 0.0

    score = 0.0
    line = lines[idx].strip().lower()

    # Strong backmatter indicators
    strong_indicators = [
        'acknowledgment', 'acknowledgement', 'about the author',
        'author bio', 'biography', 'also by', 'other books',
        'coming soon', 'next in the series', 'preview',
        'excerpt from', 'teaser', 'sneak peek',
        'discussion questions', 'reading group', 'book club',
        'notes', 'endnotes', 'bibliography', 'works cited',
        'glossary', 'index', 'appendix', 'afterword',
        'epilogue', 'colophon', 'about the publisher'
    ]

    if any(kw in line for kw in strong_indicators):
        score += 0.5

    # Position-based (last 20% more likely backmatter)
    if idx > len(lines) * 0.8:
        score += 0.2

    # After last narrative section
    if analysis.get('narrative_sections'):
        last_narrative = analysis['narrative_sections'][-1][1]
        if idx > last_narrative + 50:  # 50 line buffer
            score += 0.2

    # "The End" markers
    if line in ('the end', 'end', 'fin', 'finis'):
        score += 0.8

    return min(1.0, score)


def find_all_chapter_markers(text):
    """Find all chapter/part/act markers in the text."""
    lines = text.split('\n')
    chapter_positions = []

    for i, line in enumerate(lines):
        if patterns.matches_all_chapter_pattern(line):
            chapter_positions.append(i)

    return chapter_positions
