# allmark

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Universal eBook → Markdown converter and cleaner. Handles all formats, all artifacts, all chapter styles automatically.

Transform your entire eBook library into clean, readable Markdown files with a single command. allmark intelligently strips away the cruft—frontmatter, backmatter, headers, footers, page numbers, and metadata—leaving only the pure narrative content.

## ✨ Features

### Core Capabilities
- 📚 **Universal Format Support**: Convert 40+ formats to clean Markdown (10 verified: EPUB, HTML, DOCX, PDF, TXT, MD, RTF, ODT, LaTeX, RST)
- 🧹 **Intelligent Cleaning**: Automatically removes frontmatter, backmatter, headers, footers, page numbers
- 🔧 **OCR Repair**: Fixes broken hyphenation, ligatures, and common OCR artifacts
- 📖 **Chapter Detection**: Standardizes chapter markers across different formats
- 🎯 **Artifact Removal**: Strips ebook metadata, CSS classes, Calibre IDs, and other cruft
- 🛡️ **Safety First**: Never removes more than 50% of content (built-in safety check)
- 📊 **Progress Tracking**: SQLite database logs all conversions with statistics
- 📄 **JSONL Export**: Token-based text chunking for ML/AI training datasets
- 🎛️ **Flexible Splitting**: Paragraph-aware or strict token boundary splitting
- 🏷️ **Custom Metadata**: Add arbitrary metadata to JSONL records

### What Makes allmark Different?
- **Statistical Analysis**: Uses document structure analysis to intelligently identify and remove non-content sections
- **Dialogue-Aware**: Preserves paragraph breaks in dialogue while merging broken narrative paragraphs
- **Format Agnostic**: Same great results whether your source is a scanned PDF or a modern EPUB
- **Zero Configuration**: Works out of the box with sensible defaults
- **Batch Processing**: Convert entire libraries with a single command
- **ML-Ready Output**: Direct JSONL export with configurable chunk sizes for training datasets

## 📦 Installation

### Quick Install (pip)

```bash
pip install git+https://github.com/dcondrey/allmark.git
```

### Development Install

**Using pip:**
```bash
git clone https://github.com/dcondrey/allmark.git
cd allmark
pip install -e .
```

**Using Poetry:**
```bash
git clone https://github.com/dcondrey/allmark.git
cd allmark
poetry install
poetry shell
```

**Using Conda:**
```bash
git clone https://github.com/dcondrey/allmark.git
cd allmark
conda env create -f environment.yml
conda activate allmark
```

## 🔧 Requirements

allmark has **zero Python dependencies** - uses only Python stdlib!

### External Tools

| Tool | Purpose | Required? |
|------|---------|-----------|
| **pandoc** | EPUB, DOCX converter | ✅ Yes |
| **pdftotext** (poppler) | PDF text extraction | ✅ Yes |
| **ebook-convert** (Calibre) | FB2, MOBI fallback | ⚠️ Optional |

**PDF Extraction:**
- Uses pdftotext with `-layout` mode (preserves formatting)
- Falls back to `-raw` mode if layout fails
- Final fallback to ebook-convert if both fail

### Installing External Dependencies

<details>
<summary><b>macOS (Homebrew)</b></summary>

```bash
brew install pandoc poppler
brew install --cask calibre  # optional
```
</details>

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt-get install pandoc poppler-utils
sudo apt-get install calibre  # optional
```
</details>

<details>
<summary><b>Windows (Chocolatey)</b></summary>

```bash
choco install pandoc poppler
choco install calibre  # optional
```
</details>

## 🚀 Quick Start

### Get Help
```bash
allmark
# or
allmark --help
```

### Basic Conversion
```bash
# Convert all ebooks in a directory (with intelligent cleaning)
allmark --in /path/to/ebooks

# Output goes to same directory by default
# Verified formats: .epub, .html, .docx, .pdf, .txt, .md, .rtf, .odt, .tex, .rst
# Additional (with Calibre): .mobi, .azw3, .kf8, .fb2, .djvu
```

### Common Use Cases

<details>
<summary><b>📚 Convert entire library to Markdown</b></summary>

```bash
allmark --in ~/Books --out ~/Books-Markdown
```
</details>

<details>
<summary><b>🤖 Create ML training dataset with JSONL</b></summary>

```bash
# Convert to JSONL with 1024 token chunks
allmark --in ./books --jsonl --token-size 1024

# With custom metadata for training
allmark --in ./books --jsonl --metadata ./book_info.json
```

Example `book_info.json`:
```json
{
  "genre": "science_fiction",
  "language": "en",
  "dataset": "training_v1"
}
```
</details>

<details>
<summary><b>📄 Convert without cleaning (preserve everything)</b></summary>

```bash
allmark --in ./books --no-strip
# Keeps: frontmatter, backmatter, headers, footers, page numbers, metadata
```
</details>

<details>
<summary><b>⚡ Strict token splitting for exact chunk sizes</b></summary>

```bash
allmark --in ./books --jsonl --token-size 512 --strict-split
# Splits at exact token boundaries, ignoring paragraph breaks
```
</details>

## 📖 Usage

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--in, --input <dir>` | Input directory containing ebook files | **Required** |
| `--out, --output <dir>` | Output directory for markdown files | Same as `--in` |
| `--no-strip` | Skip cleaning (preserve all content) | Cleaning enabled |
| `--force` | Force reconversion of existing files | Skip existing |
| `--no-clean-md` | Skip cleaning existing .md files | Clean .md files |
| `--db <path>` | Conversion log database path | `./conversion_log.db` |
| `--jsonl` | Also create JSONL output with chunks | Markdown only |
| `--token-size <n>` | Max tokens per JSONL chunk | 512 |
| `--strict-split` | Split at exact token boundaries | Paragraph-aware |
| `--metadata <file>` | JSON file with custom metadata for JSONL | None |

### Examples by Use Case

```bash
# Example 1: Basic conversion with cleaning
allmark --in ./ebooks

# Example 2: Separate output directory
allmark --in ./source-books --out ./clean-markdown

# Example 3: Raw conversion (no cleaning)
allmark --in ./books --no-strip

# Example 4: Force reconversion
allmark --in ./books --force

# Example 5: Create ML training dataset
allmark --in ./books --jsonl --token-size 1024 --metadata ./metadata.json

# Example 6: Custom everything
allmark --in ./books --out ./md --db ~/conversion.db --force
```

### JSONL Output Format

When using `--jsonl`, each record contains:

```json
{
  "text": "Chunk of narrative text...",
  "chunk_index": 0,
  "total_chunks": 25,
  "token_count": 487,
  "source_file": "book.epub",
  "markdown_file": "book.md",
  "split_mode": "paragraph_aware",
  // ... plus any custom metadata from --metadata file
  "genre": "fiction",
  "language": "en"
}
```

## How It Works

allmark processes files through a comprehensive pipeline:

1. **Format Conversion**: Uses pandoc/pdftotext to convert to markdown
2. **OCR Repair**: Fixes broken hyphens, ligatures, soft hyphens
3. **Artifact Removal**: Strips images, links, CSS classes, ebook metadata
4. **Code Block Detection**: Removes non-literary code/markup blocks
5. **Header/Footer Removal**: Statistical detection of repeating elements
6. **Page Number Removal**: Multiple pattern matching
7. **TOC Removal**: Detects and removes table of contents
8. **Document Analysis**: Understands prose density and narrative structure
9. **Frontmatter/Backmatter Trimming**: Removes copyright pages, author bios, etc.
10. **Chapter Standardization**: Normalizes chapter markers to `# Chapter N`
11. **Typography Normalization**: Fixes quotes, dashes, ellipses
12. **Markdown Validation**: Ensures proper markdown formatting
13. **Paragraph Merging**: Intelligently rejoins broken paragraphs

## Project Structure

```
allmark/
├── src/
│   └── allmark/
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # CLI entry point
│       ├── cli.py            # Command-line interface
│       ├── converter.py      # Main conversion logic
│       ├── cleaners.py       # Text cleaning functions
│       ├── analyzers.py      # Document analysis
│       ├── ocr.py            # OCR artifact repair
│       └── utils.py          # Utility functions
├── setup.py                  # pip installation
├── pyproject.toml           # Modern Python packaging
├── environment.yml          # Conda environment
└── README.md                # This file
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/dcondrey/allmark.git
cd allmark

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# OR: Install with pinned dev dependencies for reproducible environment
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests

```bash
pytest
pytest --cov=allmark  # with coverage
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs**: Open an issue with details and reproduction steps
2. **Suggest features**: Share your ideas via GitHub issues
3. **Submit PRs**: Fork, create a feature branch, and submit a pull request
4. **Improve docs**: Help make the documentation clearer

See [Development Guide](#development) for setup instructions.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 David Condrey

## 💬 Support & Community

- **Issues**: [GitHub Issues](https://github.com/dcondrey/allmark/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dcondrey/allmark/discussions)
- **Documentation**: This README and inline code documentation

## 🙏 Acknowledgments

Built with:
- [Pandoc](https://pandoc.org/) - Universal document converter
- [Poppler](https://poppler.freedesktop.org/) - PDF rendering and text extraction
- Python standard library - Zero Python dependencies!

## 📊 Project Stats

- **Python Dependencies**: 0 (pure stdlib!)
- **Verified Formats**: 10 formats (EPUB, HTML, DOCX, PDF, TXT, MD, RTF, ODT, LaTeX, RST)
- **Additional Formats**: 30+ with Calibre (MOBI, AZW3, KF8, DjVu, legacy formats)
- **Cleaning Stages**: 17-stage intelligent pipeline
- **Safety Checks**: Never removes >50% of content
- **Output Formats**: Markdown, JSONL
- **Test Coverage**: Coming soon!

## 📚 Format Support

### Tier 1: Verified & Tested ✅
These formats work out-of-the-box with just Pandoc + poppler-utils:

- **EPUB** (.epub, .epub3) - Modern ebooks
- **HTML** (.html, .htm, .xhtml) - Web pages
- **DOCX** (.docx) - Microsoft Word 2007+
- **PDF** (.pdf) - Portable documents
- **TXT/MD** (.txt, .text, .md) - Plain text
- **RTF** (.rtf) - Rich text format
- **ODT** (.odt) - LibreOffice documents
- **LaTeX** (.tex, .latex) - Academic documents
- **RST** (.rst) - Python documentation

### Tier 2: With Calibre 🟡
Requires `brew install calibre` or `apt install calibre`:

- **MOBI** (.mobi) - Mobipocket/Kindle
- **AZW3/KF8** (.azw3, .kf8) - Amazon Kindle
- **FB2** (.fb2) - FictionBook (Russian format)
- **DjVu** (.djvu) - Scanned documents (also needs djvulibre)

### Tier 3: Legacy Formats ⚠️
Implemented but untested (require Calibre):
- Microsoft Reader (.lit), Sony Reader (.lrf), Palm (.pdb, .pml, .prc)
- RocketBook (.rb), TomeRaider (.tcr), XPS (.xps)
- And 15+ other obsolete formats from the 2000s

**Total**: 40+ formats supported in code, 10 verified working, 15 example files

See `examples/` directory for test files in 15 different formats!

---

<p align="center">Made with ❤️ for book lovers and data scientists</p>
