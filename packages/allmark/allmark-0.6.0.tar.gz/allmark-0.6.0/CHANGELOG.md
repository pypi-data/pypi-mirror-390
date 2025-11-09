# Changelog

All notable changes to this project will be documented in this file.

The format is based on ,
and this project adheres to .

## [0.6.0] - 2025-11-08

### Fixed

- **Frontmatter Detection**: Completely rewrote narrative start detection
  - Now finds EARLIEST legitimate narrative opening (not random mid-book matches)
  - Skips past all frontmatter markers (copyright, ISBN, domain watermarks) before searching
  - Added character name + opening line pattern (e.g., "Sir Arthur George Jennings\nListen.")
  - Added common narrative openings: "Listen.", "The [noun]", etc.
  - Fixed word boundary checking for patterns ending with spaces
  - Books now start at correct narrative beginning instead of mid-book
- **Paragraph Merging**: Fixed broken sentence merging across lines
  - Reordered logic to check for lowercase continuation BEFORE line length
  - Now correctly merges short lines like "the pain,\nchildish" → "the pain, childish"
  - Properly merges all sentences split by PDF line wrapping (~80 char lines)
  - Fixed 2,864+ broken sentences per typical book
- **Backmatter Detection**: Enhanced watermark and publisher section removal
  - Added `DOMAIN_WATERMARK` pattern for generic domain detection (*.com, *.net, *.org)
  - No longer requires explicit mentions - detects any domain watermark
  - Added specific checks for "Publisher's Note", "Publishers' Note"
  - Added "More by [Author]" section detection
  - Search starts at 70% of document (instead of 80%) for better coverage
  - All books now end with narrative text only (no watermarks/publisher content)

### Added

- **Generic Domain Watermark Pattern**: `DOMAIN_WATERMARK` in patterns.py
  - Matches any domain format: domain.com, www.domain.com, text.domain.com
  - Matches lines ending with domain extensions
  - Works for .com, .net, .org, .io, .co, .uk, .pdf
- **Enhanced Narrative Opening Patterns**: More comprehensive opening detection
  - "listen." and "listen," for literary fiction
  - "the " with word boundary for common openings like "The amber light"
  - Patterns now include both literal and boundary-checked variants

### Enhanced

- **Frontmatter Detection**: More intelligent and accurate
  - Collects ALL potential narrative starts and selects earliest
  - Requires substantial sentence length (>15 chars) to avoid false matches
  - Skips first 1% OR 10 lines (whichever is smaller) to avoid title/copyright
- **Paragraph Merging**: More aggressive and correct
  - Processes line-by-line with proper continuation detection
  - Preserves poetry, plays, dialogue, and intentional breaks
  - Merges any line ending without terminal punctuation + next line starting lowercase

## [0.5.0] - 2025-11-07

### Added

- **Multi-Strategy PDF Extraction**: 4 different extraction methods with automatic quality scoring
  - UTF-8 encoding mode for better character handling
  - Layout mode for formatted text preservation
  - No-page-breaks mode for cleaner output
  - Raw mode as final fallback
  - Quality scoring system automatically selects best extraction method
- **Play/Script Detection**: Comprehensive support for theatrical works
  - `is_stage_direction` - Detects parenthetical and bracketed stage directions
  - `is_character_name` - Detects ALL caps and Title Case character names
  - `detect_play_section` - Identifies entire play-formatted sections
  - Preserves character names, stage directions, and dialogue formatting
- **Enhanced Typography Normalization**: Comprehensive text standardization
  - ALL caps word normalization with sentence-aware case conversion
  - Preserves acronyms (3 letters or less)
  - Proper case at sentence start, lowercase mid-sentence
  - Em-dash standardization (en-dashes, double hyphens → em-dashes)
  - Enhanced ellipsis normalization (spaced dots → tight dots)
- **Centered Chapter Header Detection**: Removes centered Roman numeral headers
  - `is_centered_roman_chapter` - Detects excessive spacing + Roman numerals
  - Validates reasonable chapter numbers (I-XXX)
- **Improved Frontmatter Detection**: Narrative-first approach
  - Detects narrative openings: "when ", "it was", "there was/were", etc.
  - Prioritizes actual story start over structural headers
  - Removes "part ONE", standalone chapter numbers, TOC entries
  - More accurate content trimming across diverse book structures
- **Enhanced Backmatter Detection**: Better end-of-book cleanup
  - Watermark removal
  - ALL caps backmatter header detection (afterword, about THE author)
  - More comprehensive pattern matching


### Enhanced

- **PDF Extraction Quality**: Automatic selection of best extraction method based on:
  - Corrupted character penalization
  - Special character ratio analysis
  - Word spacing quality assessment
  - Line break and paragraph structure evaluation
  - Whitespace ratio optimization
- **Paragraph Indentation Removal**: Cleans first-line indents (2-5 spaces)
  - Preserves deeper indentation for code blocks, quotes, poetry
- **Form Feed Removal**: Removes page break characters (\f, \x0C) from PDFs
- **Quote and Apostrophe Normalization**: Already working, now documented
  - Curly quotes → straight quotes
  - Curly apostrophes → straight apostrophes


### Fixed

- **Critical**: Added missing `roman_to_int` import in `patterns.py`
- **Performance**: Refactored `normalize_caps` to avoid inefficient closure over entire text
  - Now processes line-by-line for better performance
  - Preserves ALL caps headers correctly
- **Bug**: Fixed frontmatter detection prioritizing chapter patterns over narrative
  - Changed to narrative-first approach
  - Prevents "part ONE" from being treated as content start


### Changed

- Version bump from 0.4.0 to 0.5.0
- Frontmatter detection now prioritizes narrative openings over chapter markers
- Typography normalization expanded with ALL caps handling
- Cleaning pipeline enhanced with Stage 10.5 (indentation and chapter header removal)


### Added

- **Massive Format Expansion**: Code support for 40+ ebook and document formats!
  - **10 formats verified**: epub, html, docx, PDF, TXT, MD, RTF, ODT, TEX, RST
  - **5 formats with examples**: mobi, AZW3, KF8, FB2, DjVu (require external tools)
  - **25+ legacy formats**: Implemented but untested (LIT, LRF, PDB, CHM, etc.)


#### New Pandoc-Supported Formats (15 total)

- **EPUB3** (.epub3) - Explicit EPUB3 support
- **DOC** (.doc) - Legacy Microsoft Word
- **html/xhtml** (.html, .htm, .xhtml) - Web pages
- **OpenDocument** (.odt, .ott) - LibreOffice/OpenOffice
- **Rich Text** (.rtf) - RTF documents
- **LaTeX** (.tex, .latex) - Academic documents
- **reStructuredText** (.rst) - Python documentation format
- **Plain Text** (.txt, .text) - Text files with cleaning


#### New ebook-convert Formats (25+ total)

**Kindle Formats:**
- mobi (.mobi) - Mobipocket
- AZW (.azw, .azw3, .azw4) - Amazon Kindle
- KFX (.kfx, .kf8, .kpf) - Kindle Format 10

**Legacy Reader Formats:**
- Microsoft Reader (.lit)
- Sony Reader (.lrf, .lrx)
- RocketBook (.rb, .rbz)
- Plucker (.prc)

**Desktop Formats:**
- Compiled html Help (.chm, .inf)
- TomeRaider (.tcr, .tr2, .tr3)
- XPS/OpenXPS (.xps, .oxps)

**Regional Formats:**
- Shanda Bambook (.snb) - Chinese
- Hanlin eReader (.wolf) - Chinese


#### Special Format Support

- **DjVu** (.djvu) - Scanned documents (requires djvutxt)
- **Comic Books** (.cbz, .cbr, .cbt, .cb7) - Detection with helpful error message


### Enhanced

- CLI help now lists all 40+ supported formats
- Format detection for all new extensions
- Intelligent fallback chain: Pandoc → pdftotext → ebook-convert
- Better error messages for unsupported/DRM-protected files


### Documentation

- **FORMAT_SUPPORT.md** - Comprehensive 350+ line format guide
  - Installation requirements for each format
  - Conversion method details
  - Format quality matrix
  - Troubleshooting guide
  - Format recommendations


### Changed

- `find_files` now recognizes 40+ extensions (was 6)
- `convert_file` expanded from 5 to 40+ format handlers
- Version bump from 0.3.0 to 0.4.0


### Compatibility

- Zero Python dependencies maintained
- Graceful degradation: works with just Pandoc, better with Calibre
- DRM protection respected (fails gracefully with helpful message)


### Added

- **Poetry/Verse Detection**: Automatically detects and preserves poetry sections with proper line breaks
- **Advanced Dialogue Detection**: Recognizes em-dash dialogue, quote marks, and dialogue tags
- **Smart Bracket Removal**: Preserves citations `[Smith 2020]`, footnotes `[1]`, and editorial markers `[sic]` while removing artifact brackets
- **Table Detection & Removal**: Automatically detects and removes metadata tables (markdown tables, tab-separated, space-aligned)
- **Index Detection & Removal**: Identifies and removes book indexes from end of documents
- **Better TOC Detection**: Improved table of contents detection with support for dotted leaders, tab-separated, and Roman numeral chapters
- **Improved Terminal Punctuation Detection**: Handles punctuation with quote/paren/bracket closures (e.g., `."`, `!)`, `?]`)
- **Enhanced Running Header Detection**: Tracks even/odd page headers separately to catch alternating book title/chapter title patterns
- **New Helper Functions in patterns.py**:
  - `has_terminal_punctuation` - Detects sentence-ending punctuation with closures
  - `is_dialogue_line` - Detects various dialogue formats
  - `detect_poetry_section` - Identifies verse sections
  - `is_citation_or_footnote` - Recognizes scholarly references
  - `is_table_row` - Detects table formatting
  - `is_index_entry` - Identifies index entries


### Fixed

- **Critical**: Fixed duplicate pattern definitions in `find_content_start` and `find_backmatter_start` - now use centralized `patterns.py`
- **Critical**: Fixed chapter pattern bug where `[5]` and `[42]` weren't detected (pattern only matched `[1]`)
- **Bug**: Added missing Roman numeral pattern to `CHAPTER_PATTERNS`
- **Bug**: Removed duplicate pattern and keyword definitions across multiple files
- **Bug**: Fixed tokenizer logic error where `len(word.split)` was used instead of constant 1.3
- Updated outdated comments referencing removed `pdfminer.six` dependency
- Removed obsolete `convert.py` from root directory (all code now in `src/allmark/` package)


### Improved

- **Paragraph Merging**: Now poetry-aware and dialogue-aware, prevents incorrect merging of verse and dialogue
- **Scene Break Preservation**: Whitelists valid scene breaks (`***`, `—-`, `...`) to prevent removal
- **Backmatter Detection**: Uses centralized patterns and end markers from `patterns.py`
- **Frontmatter Detection**: Uses centralized keyword list from `patterns.py`
- **Running Headers**: Better detection of chapter titles vs. book titles in alternating headers
- **Bracket Removal**: Smart logic preserves footnotes and citations while removing artifacts


### Changed

- Bumped version from 0.2.0 to 0.3.0
- Cleaning pipeline now includes:
  - Stage 6.5: Table removal
  - Stage 9.5: Index section removal
  - Enhanced stage 15: Artifact line removal with whitelisting
  - Enhanced stage 16: Poetry-aware paragraph merging
- All pattern definitions now centralized in `patterns.py`


### Performance

- Reduced code duplication by centralizing all pattern definitions
- More efficient pattern matching using pre-compiled regex from `patterns.py`


### Added

- **jsonl Export**: Token-based text chunking for ML/AI training datasets
  - `—jsonl` flag to enable jsonl output alongside Markdown
  - `—token-size` to configure chunk size (default: 512 tokens)
  - `—strict-split` for exact token boundaries vs paragraph-aware splitting
  - `—metadata` to load custom metadata from json file
- **Enhanced PDF Support**: Improved pdftotext usage
  - Layout mode (preserves formatting) with raw mode fallback
  - Better text quality from PDFs
- **Custom Metadata**: Add arbitrary metadata to all jsonl records via json file
- New module: `tokenizer.py` for text splitting and token counting
- New module: `pdf_extract.py` for improved PDF text extraction


### Changed

- PDF extraction now tries `-layout` mode first, falls back to `-raw` mode
- jsonl records include comprehensive metadata (source file, chunk info, split mode)
- Documentation updated with jsonl usage examples


### Improved

- Better error messages and validation for jsonl options
- Progress output shows chunking statistics
- Still **zero Python dependencies** - pure stdlib!


### Added

- Initial release
- Universal eBook to Markdown conversion (epub, docx, PDF, FB2, mobi)
- Intelligent document cleaning and artifact removal
- OCR artifact repair (broken hyphenation, ligatures)
- Automatic frontmatter/backmatter detection and removal
- Statistical header/footer detection and removal
- Page number removal across multiple formats
- Table of contents detection and removal
- Chapter marker standardization
- Paragraph merging with dialogue awareness
- Typography normalization
- SQLite-based conversion logging
- CLI with `—no-strip` option for raw conversion
- User-friendly help screen with examples
- Smart defaults: `—out` defaults to `—in` directory
- Input validation with helpful error messages
- Support for pip, poetry, and conda installation
- Comprehensive documentation
