# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-07

### Added
- **Massive Format Expansion**: Code support for 40+ ebook and document formats!
  - **10 formats verified**: EPUB, HTML, DOCX, PDF, TXT, MD, RTF, ODT, TEX, RST
  - **5 formats with examples**: MOBI, AZW3, KF8, FB2, DjVu (require external tools)
  - **25+ legacy formats**: Implemented but untested (LIT, LRF, PDB, CHM, etc.)

#### New Pandoc-Supported Formats (15 total)
- **EPUB3** (.epub3) - Explicit EPUB3 support
- **DOC** (.doc) - Legacy Microsoft Word
- **HTML/XHTML** (.html, .htm, .xhtml) - Web pages
- **OpenDocument** (.odt, .ott) - LibreOffice/OpenOffice
- **Rich Text** (.rtf) - RTF documents
- **LaTeX** (.tex, .latex) - Academic documents
- **reStructuredText** (.rst) - Python documentation format
- **Plain Text** (.txt, .text) - Text files with cleaning

#### New ebook-convert Formats (25+ total)
**Kindle Formats:**
- MOBI (.mobi) - Mobipocket
- AZW (.azw, .azw3, .azw4) - Amazon Kindle
- KFX (.kfx, .kf8, .kpf) - Kindle Format 10

**Legacy Reader Formats:**
- Microsoft Reader (.lit)
- Sony Reader (.lrf, .lrx)
- RocketBook (.rb, .rbz)
- Palm OS (.pdb, .pml, .pmlz, .prc)
- Plucker (.prc)

**Desktop Formats:**
- Compiled HTML Help (.chm, .inf)
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
- `find_files()` now recognizes 40+ extensions (was 6)
- `convert_file()` expanded from 5 to 40+ format handlers
- Version bump from 0.3.0 to 0.4.0

### Compatibility
- Zero Python dependencies maintained
- Graceful degradation: works with just Pandoc, better with Calibre
- DRM protection respected (fails gracefully with helpful message)

---

## [0.3.0] - 2025-11-07

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
  - `has_terminal_punctuation()` - Detects sentence-ending punctuation with closures
  - `is_dialogue_line()` - Detects various dialogue formats
  - `detect_poetry_section()` - Identifies verse sections
  - `is_citation_or_footnote()` - Recognizes scholarly references
  - `is_table_row()` - Detects table formatting
  - `is_index_entry()` - Identifies index entries

### Fixed
- **Critical**: Fixed duplicate pattern definitions in `find_content_start()` and `find_backmatter_start()` - now use centralized `patterns.py`
- **Critical**: Fixed chapter pattern bug where `[5]` and `[[42]]` weren't detected (pattern only matched `[1]`)
- **Bug**: Added missing Roman numeral pattern to `CHAPTER_PATTERNS`
- **Bug**: Removed duplicate pattern and keyword definitions across multiple files
- **Bug**: Fixed tokenizer logic error where `len(word.split())` was used instead of constant 1.3
- Updated outdated comments referencing removed `pdfminer.six` dependency
- Removed obsolete `convert.py` from root directory (all code now in `src/allmark/` package)

### Improved
- **Paragraph Merging**: Now poetry-aware and dialogue-aware, prevents incorrect merging of verse and dialogue
- **Scene Break Preservation**: Whitelists valid scene breaks (`***`, `---`, `...`) to prevent removal
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

---

## [0.2.0] - 2025-11-07

### Added
- **JSONL Export**: Token-based text chunking for ML/AI training datasets
  - `--jsonl` flag to enable JSONL output alongside Markdown
  - `--token-size` to configure chunk size (default: 512 tokens)
  - `--strict-split` for exact token boundaries vs paragraph-aware splitting
  - `--metadata` to load custom metadata from JSON file
- **Enhanced PDF Support**: Improved pdftotext usage
  - Layout mode (preserves formatting) with raw mode fallback
  - Better text quality from PDFs
- **Custom Metadata**: Add arbitrary metadata to all JSONL records via JSON file
- New module: `tokenizer.py` for text splitting and token counting
- New module: `pdf_extract.py` for improved PDF text extraction

### Changed
- PDF extraction now tries `-layout` mode first, falls back to `-raw` mode
- JSONL records include comprehensive metadata (source file, chunk info, split mode)
- Documentation updated with JSONL usage examples

### Improved
- Better error messages and validation for JSONL options
- Progress output shows chunking statistics
- Still **zero Python dependencies** - pure stdlib!

## [0.1.0] - 2025-11-07

### Added
- Initial release
- Universal eBook to Markdown conversion (EPUB, DOCX, PDF, FB2, MOBI)
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
- CLI with `--no-strip` option for raw conversion
- User-friendly help screen with examples
- Smart defaults: `--out` defaults to `--in` directory
- Input validation with helpful error messages
- Support for pip, poetry, and conda installation
- Comprehensive documentation
