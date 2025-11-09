# Example eBooks

This folder contains sample eBooks in **14 different formats** for testing allmark's format support.

All files are "Alice's Adventures in Wonderland" by Lewis Carroll (Public Domain).


## Available Formats


### ✅ Modern eBook Formats

- **alice.epub** - EPUB2/3 (185 KB) - Project Gutenberg
- **alice.azw3** - Amazon Kindle AZW3 (8.4 KB) - Standard Ebooks
- **alice.mobi** - Mobipocket/Kindle (236 KB) - Project Gutenberg
- **alice.kf8** - Kindle Format 8 (251 KB) - Project Gutenberg


### ✅ Document Formats

- **alice.html** - html (166 KB) - Project Gutenberg
- **alice.pdf** - PDF (87 KB) - Adobe Sample
- **sample.docx** - Microsoft Word (11 KB) - Pandoc-generated
- **alice.fb2** - FictionBook 2.0 (53 KB) - LinguaBooster
- **alice.odt** - OpenDocument (170 KB) - Pandoc-converted
- **alice.rtf** - Rich Text Format (424 KB) - Pandoc-converted


### ✅ Academic Formats

- **alice.tex** - LaTeX (172 KB) - Pandoc-converted
- **alice.rst** - reStructuredText (184 KB) - Pandoc-converted


### ✅ Scanned Documents

- **alice.djvu** - DjVu (1.8 MB) - Internet Archive


### ✅ Plain Text

- **alice.txt** - Plain text (148 KB) - Project Gutenberg
- **alice.md** - Markdown (148 KB) - Copy of txt


## Usage

Convert all examples (creates 14 markdown files):

```bash
allmark —in examples —out examples/output

Convert with jsonl output for ML/AI training:

```bash
allmark —in examples —out examples/output —jsonl —token-size 512

Convert without cleaning (raw conversion):

```bash
allmark —in examples —out examples/output —no-strip

Test specific format:

```bash


# epub to markdown

mkdir test_epub && cp examples/alice.epub test_epub/ allmark —in test_epub —out output_epub


# html to markdown

mkdir test_html && cp examples/alice.html test_html/ allmark —in test_html —out output_html


# Kindle to markdown

mkdir test_kindle && cp examples/alice.mobi test_kindle/ allmark —in test_kindle —out output_kindle


## Format Quality Comparison

All formats were tested with allmark. Results:


## What Gets Cleaned

allmark's cleaning pipeline removes common ebook artifacts:

- Project Gutenberg license text (frontmatter)
- "Produced by..." credits (frontmatter)
- Table of Contents
- "*** END OF project gutenberg..." (backmatter)
- Page numbers (from PDFs)
- Running headers/footers
- Metadata tables
- Index sections
- Artifact brackets `pg 42`, `Illustration`


### ✅ Preserved

- All chapter text
- Chapter headings (standardized to `# Chapter N`)

- Dialogue (properly formatted)
- Poetry/verse (line breaks maintained)
- Italics and emphasis
- Citations and footnotes `[1]`, `[Smith 2020]`
- Editorial markers `[sic]`, `[emphasis added]`


## Testing Format Support

Want to verify a format works? Use this workflow:

```bash


# 1. Create test directory

mkdir test_format
cp your_book.format test_format/


# 2. Convert

allmark —in test_format —out test_output —no-strip


# 3. Check output quality

cat test_output/your_book.md | head -50


# 4. If good, convert with cleaning

allmark —in test_format —out test_output_clean


## Format Support Requirements


### No Additional Tools Needed

EPUB, docx, html, TXT, MD, RTF, ODT, TEX, RST - Work with just Pandoc


### Requires poppler-utils

PDF - Needs `pdftotext` command (`brew install poppler`)


### Requires Calibre

MOBI, AZW, AZW3, KF8, FB2 (fallback) - Needs `ebook-convert` (`brew install calibre`)


### Requires djvulibre

DjVu - Needs `djvutxt` command (`brew install djvulibre`)


## License

All example files are either:
- **Public Domain** (alice.epub from Project Gutenberg)
- **Sample/Demo files** (alice.pdf from Adobe)
- **Created for testing** (sample.docx)

Free to use, modify, and distribute.
