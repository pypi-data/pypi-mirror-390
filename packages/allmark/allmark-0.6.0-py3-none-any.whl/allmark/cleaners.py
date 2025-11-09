"""Text cleaning utilities."""

from collections import Counter

from .utils import looks_like_code, looks_like_junk, roman_to_int
from .analyzers import analyze_document_structure, find_all_chapter_markers
from . import patterns


def detect_repeating_headers_footers(text):
    """Detect and remove statistically repeating headers/footers with improved detection."""
    lines = text.split('\n')

    # Split into page-like chunks (every ~50 lines or at form feeds)
    pages = []
    current_page = []
    line_count = 0

    for line in lines:
        if '\f' in line or line_count >= 50:
            if current_page:
                pages.append(current_page)
            current_page = []
            line_count = 0
        current_page.append(line)
        line_count += 1

    if current_page:
        pages.append(current_page)

    # Count occurrences of top and bottom lines
    top_lines = Counter()
    bottom_lines = Counter()
    even_headers = Counter()
    odd_headers = Counter()

    for idx, page in enumerate(pages):
        if page:
            top = page[0].strip()
            bottom = page[-1].strip()

            top_lines[top] += 1
            bottom_lines[bottom] += 1

            # Track even/odd page headers separately
            if idx % 2 == 0:
                even_headers[top] += 1
            else:
                odd_headers[top] += 1

    # Identify repeating headers/footers (appear 4+ times)
    victims = set()

    # Check top headers
    for line, count in top_lines.items():
        if count >= 4 and (patterns.HEADER_PAGE_NUMBER.match(line) or len(line) < 80):
            # Not a chapter heading
            if not patterns.matches_all_chapter_pattern(line):
                victims.add(line)

    # Check bottom footers
    for line, count in bottom_lines.items():
        if count >= 4 and (patterns.HEADER_PAGE_NUMBER.match(line) or len(line) < 80):
            victims.add(line)

    # Check for alternating headers (even pages: chapter title, odd pages: book title)
    for line, count in even_headers.items():
        if count >= 3 and len(line) < 80 and not patterns.matches_all_chapter_pattern(line):
            victims.add(line)

    for line, count in odd_headers.items():
        if count >= 3 and len(line) < 80 and not patterns.matches_all_chapter_pattern(line):
            victims.add(line)

    # Remove victim lines
    if victims:
        cleaned = [line for line in lines if line.strip() not in victims]
        return '\n'.join(cleaned)

    return text


def detect_and_remove_code_blocks(text):
    """Detect and remove blocks of code/markup that aren't literary content."""
    lines = text.split('\n')
    cleaned_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this starts a code block
        if looks_like_code(line):
            # Count consecutive code-like lines
            code_block_start = i
            code_count = 0
            j = i

            while j < len(lines) and j < i + 20:  # Max 20 line lookahead
                if looks_like_code(lines[j]) or not lines[j].strip():
                    code_count += 1
                    j += 1
                else:
                    break

            # If we have 3+ consecutive code lines, it's likely a code block
            if code_count >= 3:
                # Skip entire block
                i = j
                continue

        # Not a code block, keep the line
        cleaned_lines.append(line)
        i += 1

    return '\n'.join(cleaned_lines)


def validate_and_fix_formatting(text):
    """Validate markdown formatting and fix common issues."""
    lines = text.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Fix headers with missing space: "#Chapter" -> "# Chapter"
        if line.startswith('#') and len(line) > 1 and line[1] != ' ':
            level = 0
            for c in line:
                if c == '#':
                    level += 1
                else:
                    break
            if level > 0 and level <= 6:
                line = '#' * level + ' ' + line[level:].strip()

        # Fix emphasis markers with spaces: "* text *" -> "*text*"
        line = patterns.EMPHASIS_STAR_SPACE.sub(r'*\1*', line)
        line = patterns.EMPHASIS_UNDER_SPACE.sub(r'_\1_', line)

        # Fix broken emphasis: multiple stars/underscores
        line = patterns.MULTIPLE_STARS.sub('***', line)  # Normalize to 3
        line = patterns.MULTIPLE_UNDERS.sub('___', line)

        # Remove trailing whitespace
        line = line.rstrip()

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def remove_toc_clusters(text):
    """Detect and remove table of contents clusters."""
    lines = text.split('\n')
    clusters = []
    i = 0

    while i < len(lines):
        j = i
        score = 0
        count = 0

        while j < len(lines):
            ln = lines[j].strip()
            if not ln:
                if count >= 5 and score >= 4:
                    clusters.append((i, j))
                break

            # TOC patterns
            toc_score = 0

            # Ends with page number
            if patterns.TOC_PAGE_NUMBER.search(ln):
                toc_score += 1

            # Dotted leaders: "Chapter One ........ 10"
            if patterns.TOC_DOTTED_LEADERS.search(ln):
                toc_score += 2

            # Tab-separated: "Chapter One\t\t\t42"
            if '\t' in ln and patterns.TOC_DOTTED_LEADERS.search(ln):
                toc_score += 2

            # Roman numeral chapters: "I. Introduction"
            if patterns.TOC_ROMAN_CHAPTER.match(ln):
                toc_score += 1

            # Multi-line TOC entries (indented subentries)
            if ln.startswith('    ') or ln.startswith('\t'):
                toc_score += 1

            score += toc_score

            if len(ln) <= 80:
                count += 1
            else:
                break
            j += 1

        i = max(i + 1, j)

    if clusters:
        mask = [True] * len(lines)
        for a, b in clusters:
            for k in range(a, b + 1):
                if k < len(mask):
                    mask[k] = False
        return '\n'.join([ln for k, ln in enumerate(lines) if mask[k]])

    return text


def remove_tables(text):
    """Detect and remove tables (usually metadata artifacts)."""
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        # Check if this starts a table block
        if patterns.is_table_row(lines[i]):
            # Count consecutive table rows
            j = i
            while j < len(lines) and (patterns.is_table_row(lines[j]) or not lines[j].strip()):
                j += 1

            # If 3+ table rows, it's likely a table - skip it
            table_rows = sum(1 for k in range(i, j) if patterns.is_table_row(lines[k]))
            if table_rows >= 3:
                i = j
                continue

        result.append(lines[i])
        i += 1

    return '\n'.join(result)


def remove_index_section(text):
    """Detect and remove index section from end of book."""
    lines = text.split('\n')

    # Look for "Index" header in last 20% of document
    search_start = max(0, int(len(lines) * 0.8))

    for i in range(search_start, len(lines)):
        stripped = lines[i].strip()

        # Found index header
        if patterns.INDEX_HEADER.match(stripped):
            # Check if following lines are index entries
            index_entry_count = 0
            for j in range(i + 1, min(i + 20, len(lines))):
                if patterns.is_index_entry(lines[j]):
                    index_entry_count += 1

            # If 5+ index entries follow, remove from header onwards
            if index_entry_count >= 5:
                return '\n'.join(lines[:i])

    return text


def remove_page_numbers(text):
    """Remove page numbers in various formats."""
    lines = text.split('\n')
    cleaned = []

    for line in lines:
        if not patterns.is_page_number(line) and not looks_like_junk(line):
            cleaned.append(line)

    return '\n'.join(cleaned)


def aggressive_artifact_removal(text):
    """Remove ALL ebook/epub/pandoc artifacts."""

    # Remove images and links
    text = patterns.IMAGE_MARKDOWN.sub('', text)
    text = patterns.LINK_MARKDOWN.sub('', text)
    text = patterns.URL_PATTERN.sub('', text)

    # Remove ALL class/ID/style markers
    text = patterns.CLASS_MARKER.sub('', text)
    text = patterns.CLASS_BRACKET.sub(r'_\1_', text)
    text = patterns.ID_MARKER.sub('', text)
    text = patterns.STYLE_ATTR.sub('', text)
    text = patterns.HEIGHT_ATTR.sub('', text)
    text = patterns.WIDTH_ATTR.sub('', text)
    text = patterns.CLASS_ATTR.sub('', text)

    # Remove standalone markers on their own lines
    text = patterns.STANDALONE_CLASS.sub('', text)
    text = patterns.STANDALONE_BRACKET.sub('', text)

    # Remove Pandoc/ePub artifacts
    text = patterns.PANDOC_HTML.sub('', text)
    text = patterns.EPUB_HTML.sub('', text)
    text = patterns.EPUB_TYPE.sub('', text)

    # Remove calibre artifacts
    text = patterns.CALIBRE_ID.sub('', text)
    text = patterns.CALIBRE_CLASS.sub('', text)

    # Remove div/span markers
    text = patterns.DIV_MARKER.sub('', text)
    text = patterns.STANDALONE_DIV.sub('', text)

    # Remove "copy" artifacts
    text = patterns.COPY_PREFIX.sub('', text)
    text = text.replace('©', '')
    text = patterns.COPYRIGHT_YEAR.sub('', text)

    # Remove HTML tags
    text = patterns.HTML_TAG.sub('', text)

    # Remove empty brackets/parens
    text = patterns.EMPTY_BRACKETS.sub('', text)
    text = patterns.EMPTY_PARENS.sub('', text)

    # Fix split capitals like "F[OR A MAN]" -> "FOR A MAN"
    text = patterns.SPLIT_CAPITALS.sub(r'\1\2', text)

    # Smart bracket removal: preserve citations/footnotes, remove artifacts
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Find all bracketed content in this line
        bracket_matches = list(patterns.REMAINING_BRACKETS.finditer(line))

        if not bracket_matches:
            cleaned_lines.append(line)
            continue

        # Process each bracket from right to left (to preserve positions)
        for match in reversed(bracket_matches):
            full_match = match.group(0)
            inner = match.group(1)
            start, end = match.span()

            # Preserve citations and footnotes
            if patterns.is_citation_or_footnote(full_match):
                continue

            # Preserve stage directions (keep brackets for stage directions)
            if patterns.is_stage_direction(full_match):
                continue

            # Empty brackets - remove entirely
            if not inner.strip():
                line = line[:start] + line[end:]
                continue

            # Short text (1-50 chars) - convert to emphasis
            if len(inner) <= 50 and not any(c in inner for c in '[]{}()'):
                # Check context - if surrounded by whitespace or punctuation
                before_ok = start == 0 or line[start-1] in ' \t\n'
                after_ok = end >= len(line) or line[end] in ' \t\n.,;:!?)'

                if before_ok or after_ok:
                    line = line[:start] + f'_{inner}_' + line[end:]
                    continue

            # Default: remove brackets but keep content
            line = line[:start] + inner + line[end:]

        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    return text


def find_content_start(text):
    """Find where narrative begins by looking for first Part/Act/Chapter markers."""
    lines = text.split('\n')

    # First priority: Look for strong narrative opening phrases
    # These should be at the START of the line and be EARLY in the document
    # We collect ALL matches and choose the earliest one that looks legitimate
    narrative_openings = [
        ('in the beginning', True),  # (pattern, requires_word_boundary)
        ('it was', True),
        ('once upon a time', False),
        ('the year was', False),
        ('it is a truth', False),  # Pride and Prejudice
        ('when ', True),  # "when i was", "when he was", "when she was", etc.
        ('there was', True),
        ('there were', True),
        ('the ', True),  # Very common: "The amber light", "The boy", etc.
        ('listen.', False),  # Common literary opening
        ('listen,', False),
    ]

    # Collect all potential narrative starts
    potential_starts = []

    # Find last frontmatter marker (copyright, domain watermarks, etc.)
    last_frontmatter_idx = 0
    for i, line in enumerate(lines[:min(200, len(lines))]):  # Only check first 200 lines
        stripped = line.strip().lower()

        # Check for domain watermarks (e.g., anysite.com)
        if patterns.DOMAIN_WATERMARK.search(stripped):
            last_frontmatter_idx = i
            continue

        # Common frontmatter markers
        if any(marker in stripped for marker in ['copyright', 'isbn', 'published', 'reserved', 'table of contents', 'dedication']):
            last_frontmatter_idx = i

    for i, line in enumerate(lines):
        stripped = line.strip()
        lower = stripped.lower()

        # Skip if before last frontmatter marker + 2 lines
        if i < last_frontmatter_idx + 2:
            continue

        # Check for character name followed by narrative (literary fiction pattern)
        # Example: "Sir Arthur George Jennings" followed by "Listen."
        if i > 0 and len(stripped) > 3 and len(stripped) < 50:
            # Check if this looks like a character name
            words = stripped.split()
            if (len(words) >= 2 and
                all(w[0].isupper() for w in words if len(w) > 0) and
                not any(kw in lower for kw in ['chapter', 'part', 'book', 'contents', 'copyright', 'dedication'])):
                # Check if next line starts narrative
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip().lower()
                    if any(next_line.startswith(opening[0]) for opening in narrative_openings):
                        # Found character name + narrative opening
                        potential_starts.append((i, 'character_name'))

        # Check for strong narrative openings
        for opening, needs_boundary in narrative_openings:
            if lower.startswith(opening):
                if needs_boundary:
                    # Verify word boundary
                    # If opening ends with space, next char can be anything (boundary already satisfied)
                    # If opening doesn't end with space, next char must be boundary char
                    if opening.endswith(' '):
                        # Word boundary already in pattern (e.g., "the ", "when ")
                        if len(stripped) > 15:
                            potential_starts.append((i, f'opening:{opening[0]}'))
                    else:
                        # Need to check boundary (e.g., "it was" should not match "it wasn't")
                        if len(stripped) == len(opening) or stripped[len(opening)] in ' .,;:!?':
                            if len(stripped) > 15:
                                potential_starts.append((i, f'opening:{opening[0]}'))
                else:
                    # Direct match OK
                    if len(stripped) > 10:
                        potential_starts.append((i, f'opening:{opening[0]}'))

    # Return the EARLIEST match if we found any
    if potential_starts:
        # Sort by line number and return the first
        potential_starts.sort(key=lambda x: x[0])
        return potential_starts[0][0]

    # Third priority: Remove OceanofPDF watermark sections
    # These often appear between frontmatter and narrative
    for i, line in enumerate(lines):
        if 'oceanofpdf' in line.lower():
            # Check if next few lines look like narrative
            for j in range(i+1, min(i+10, len(lines))):
                stripped = lines[j].strip()
                if stripped and len(stripped) > 50 and stripped[0].isupper():
                    # Found narrative after OceanofPDF marker
                    return j

    # Fallback: Use keyword-based detection
    narrative_count = 0
    start_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        # Skip frontmatter
        if any(kw in stripped.lower() for kw in patterns.FRONTMATTER_KEYWORDS):
            narrative_count = 0
            continue

        # Look for substantial narrative lines
        if len(stripped) > 150 and stripped[0].isupper() and '.' in stripped:
            narrative_count += 1
            if narrative_count >= 3 and start_idx is None:
                start_idx = i - 2
                break
        elif len(stripped) < 100:
            narrative_count = 0

    # SAFETY: Don't remove more than 10% of file
    if start_idx and start_idx > len(lines) * 0.1:
        start_idx = int(len(lines) * 0.05)

    return start_idx if start_idx else 0


def merge_broken_paragraphs(text):
    """Intelligently merge broken paragraphs while preserving dialogue, poetry, and intentional breaks."""
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        current = lines[i].rstrip()

        # Empty lines, headers, or special markers - keep as-is
        if not current or current.startswith('#') or current in ('***', '---', '…'):
            result.append(current)
            i += 1
            continue

        # Check for poetry section
        poetry_lines = patterns.detect_poetry_section(lines, i)
        if poetry_lines > 0:
            # Preserve poetry line breaks
            for j in range(i, min(i + poetry_lines, len(lines))):
                result.append(lines[j].rstrip())
            i += poetry_lines
            continue

        # Check for play/script section
        play_lines = patterns.detect_play_section(lines, i)
        if play_lines > 0:
            # Preserve play formatting (character names, stage directions, dialogue)
            for j in range(i, min(i + play_lines, len(lines))):
                result.append(lines[j].rstrip())
            i += play_lines
            continue

        # Check if we should merge with next line
        if i < len(lines) - 1:
            next_line = lines[i + 1].lstrip()
            prev_line = lines[i - 1] if i > 0 else None

            # Don't merge if current line ends with terminal punctuation
            if patterns.has_terminal_punctuation(current):
                result.append(current)
                i += 1
                continue

            # Don't merge if next line is dialogue
            if patterns.is_dialogue_line(next_line, prev_line=current):
                result.append(current)
                i += 1
                continue

            # Don't merge if next line is empty, header, or special
            if not next_line or next_line.startswith('#') or next_line in ('***', '---'):
                result.append(current)
                i += 1
                continue

            # Merge if next line starts with lowercase or continuation punctuation
            # This handles broken paragraphs like "the pain,\nchildish"
            if next_line and (next_line[0].islower() or next_line[0] in ',.;:)]}'):
                # Merge with space
                result.append(current + ' ' + next_line)
                i += 2
                continue

            # Don't merge if current line is very short (likely intentional break)
            # BUT: moved this check AFTER the lowercase check so we still merge
            # broken sentences even if the first part is short
            if len(current) < 40:
                result.append(current)
                i += 1
                continue

        # Default: keep line as-is
        result.append(current)
        i += 1

    return '\n'.join(result)


def find_backmatter_start(text):
    """Find where backmatter begins by looking for last chapter end or backmatter markers."""
    lines = text.split('\n')

    # First: Try to find where last chapter ends
    chapter_positions = find_all_chapter_markers(text)

    if len(chapter_positions) >= 2:
        # Calculate average chapter length
        chapter_lengths = []
        for i in range(len(chapter_positions) - 1):
            chapter_lengths.append(chapter_positions[i+1] - chapter_positions[i])

        avg_chapter_length = sum(chapter_lengths) / len(chapter_lengths)
        last_chapter_start = chapter_positions[-1]

        # Estimate where last chapter should end
        estimated_end = int(last_chapter_start + avg_chapter_length)

        # Look for actual end (substantial narrative gap or backmatter keyword)
        # Search from estimated end to document end
        for i in range(estimated_end, len(lines)):
            stripped = lines[i].strip().lower()

            # Check for backmatter keywords
            if any(kw in stripped for kw in patterns.BACKMATTER_KEYWORDS):
                return i

            # Check for end markers
            if stripped in patterns.END_MARKERS or stripped == '***':
                return i + 1

        # If no explicit marker, use estimated end + 10% buffer
        if estimated_end < len(lines):
            return min(int(estimated_end * 1.1), len(lines) - 1)

    # Fallback: Use pattern matching in last 30% of document
    search_start = max(0, int(len(lines) * 0.7))

    # First pass: Look for website watermarks and publisher markers (most reliable)
    for i in range(search_start, len(lines)):
        stripped = lines[i].strip().lower()

        # Generic domain watermark detection (e.g., "oceanofpdf.com", "ebookbike.com", etc.)
        # Matches: domain.com, www.domain.com, text.domain.com, or lines ending with .com/.net/.org
        if patterns.DOMAIN_WATERMARK.search(stripped):
            return i

        # Also catch lines that contain ONLY a domain (possibly with spaces)
        if stripped and '.' in stripped and len(stripped.split()) == 1:
            # Check if it looks like a domain (has .com, .net, etc.)
            if any(ext in stripped for ext in ['.com', '.net', '.org', '.io', '.co', '.uk', '.pdf']):
                return i

        # Publisher markers
        if stripped == "publisher's note" or stripped == "publishers' note":
            return i

        # "About the Author" section
        if stripped in ['about the author', 'about the authors']:
            return i

        # "Also by" / "More by" sections
        if stripped.startswith('also by ') or stripped.startswith('more by '):
            return i

    # Second pass: Search backwards for backmatter keywords
    for i in range(len(lines) - 1, search_start, -1):
        stripped = lines[i].strip()
        lower = stripped.lower()

        # Check backmatter keywords
        if any(kw in lower for kw in patterns.BACKMATTER_KEYWORDS):
            # Make sure this isn't just a passing reference
            # Check if it's a section header (short line, possibly all caps)
            if len(stripped) < 100:
                return i

        # Check backmatter patterns
        for pattern in patterns.BACKMATTER_PATTERNS:
            if pattern.match(stripped):
                return i

    # Third pass: Look for all-caps section headers
    for i in range(search_start, len(lines)):
        stripped = lines[i].strip()
        if stripped.isupper() and len(stripped) > 3 and len(stripped) < 100:
            lower = stripped.lower()
            if any(kw in lower for kw in ['afterword', 'about the author', 'acknowledgment', 'also by', 'more by']):
                return i

    return None


def standardize_chapters(text):
    """Convert chapter markers to # Chapter N format where they exist."""
    lines = text.split('\n')
    result = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            result.append(line)
            continue

        converted = False

        # Pattern: [[1]] or [1]
        match = patterns.CHAPTER_BRACKET.match(stripped)
        if match:
            result.append(f"# Chapter {match.group(1)}")
            converted = True

        # Pattern: "Chapter 1" or "CHAPTER 1"
        if not converted:
            match = patterns.CHAPTER_WORD.match(stripped)
            if match:
                num = match.group(2)
                # Convert roman numerals to numbers
                if patterns.CHAPTER_ROMAN.match(num):
                    num = str(roman_to_int(num))
                result.append(f"# Chapter {num}")
                converted = True

        # Pattern: Just a number (1-50 range, check context)
        if not converted:
            match = patterns.CHAPTER_NUMBER.match(stripped)
            if match and 1 <= int(match.group(1)) <= 50:
                # Check if next line looks like narrative
                if i + 1 < len(lines) and len(lines[i+1].strip()) > 50:
                    result.append(f"# Chapter {match.group(1)}")
                    converted = True

        # Pattern: Roman numerals alone
        if not converted:
            match = patterns.CHAPTER_ROMAN.match(stripped)
            if match:
                try:
                    num = roman_to_int(match.group(1))
                    if 1 <= num <= 50:
                        result.append(f"# Chapter {num}")
                        converted = True
                except:
                    pass

        if not converted:
            result.append(line)

    return '\n'.join(result)
