# Format Support Guide

allmark supports **40+ ebook and document formats** through a combination of Pandoc (direct conversion) and Calibre's ebook-convert (fallback for proprietary formats).

## Support Tiers

**Tier 1: Verified (10 formats)** ✅
- Tested with example files
- Work with standard installation (Pandoc + poppler-utils)
- Production-ready

**Tier 2: Implemented (5 formats)** 🟡
- Code exists and should work
- Require additional tools (Calibre, djvulibre)
- Not yet tested (no examples or tools missing)

**Tier 3: Legacy Support (25+ formats)** ⚠️
- Code implemented
- Require Calibre
- Untested (hard to find test files)
- May or may not work in practice

---

## Tier 1: Verified Formats ✅

These formats have been tested with example files and confirmed working:

### Modern eBook Formats
- **EPUB** (.epub, .epub3) - Electronic Publication (EPUB2 and EPUB3) ✅ Tested
- **HTML** (.html, .htm, .xhtml) - Web pages and XHTML documents ✅ Tested

### Microsoft Office
- **Word** (.docx) - Microsoft Word 2007+ ✅ Tested
- **OpenDocument** (.odt) - LibreOffice/OpenOffice text documents ✅ Tested
- **Rich Text** (.rtf) - Rich Text Format ✅ Tested

### Academic & Technical
- **LaTeX** (.tex, .latex) - LaTeX documents ✅ Tested
- **reStructuredText** (.rst) - Python documentation format ✅ Tested

### Plain Text
- **Text** (.txt, .text) - Plain text files ✅ Tested
- **Markdown** (.md) - Already in markdown (just cleaned) ✅ Tested

### PDF
- **PDF** (.pdf) - Portable Document Format ✅ Tested
  - Uses pdftotext (from poppler-utils)
  - Layout mode with raw mode fallback

---

## Tier 2: Implemented but Untested 🟡

These formats have code implementation and example files, but require external tools:

### Kindle Formats (Require Calibre)
- **Mobipocket** (.mobi) - Original Kindle format 🟡 Have example
- **AZW3** (.azw3) - Amazon Kindle format 🟡 Have example
- **KF8** (.kf8) - Kindle Format 8 🟡 Have example

### Other Formats
- **FictionBook** (.fb2) - Russian XML-based ebook format 🟡 Have example (had XML error)
- **DjVu** (.djvu) - Scanned document format 🟡 Have example
  - **Requires**: `djvutxt` from djvulibre package
  - **Install**: `brew install djvulibre` (macOS) or `apt install djvulibre-bin` (Linux)

---

## Tier 3: Legacy Format Support ⚠️

These formats are implemented in code but **NOT TESTED** (no example files available):

### Kindle Formats (Require Calibre)
- **AZW** (.azw, .azw4) - Older Amazon Kindle formats ⚠️ No examples
- **KFX** (.kfx, .kpf) - Kindle Format 10 ⚠️ No examples

### Legacy Mobile Readers (Require Calibre)
- **Microsoft Reader** (.lit) - Microsoft eBook format ⚠️ No examples
- **Sony Reader** (.lrf, .lrx) - Sony proprietary formats ⚠️ No examples
- **RocketBook** (.rb, .rbz) - RocketBook format ⚠️ No examples
- **Palm** (.pdb, .pml, .pmlz, .prc) - Palm OS ebooks ⚠️ No examples

### Legacy Desktop Readers (Require Calibre)
- **Compiled HTML** (.chm, .inf) - Windows Help format ⚠️ No examples
- **TomeRaider** (.tcr, .tr2, .tr3) - TomeRaider ebook format ⚠️ No examples
- **XPS/OpenXPS** (.xps, .oxps) - XML Paper Specification ⚠️ No examples

### Regional Formats (Require Calibre)
- **Shanda Bambook** (.snb) - Chinese ebook format ⚠️ No examples
- **Hanlin eReader** (.wolf) - Chinese ebook reader format ⚠️ No examples

### Legacy Office Formats
- **Word 97-2003** (.doc) - Legacy Microsoft Word ⚠️ No examples
- **OpenDocument Template** (.ott) - LibreOffice templates ⚠️ No examples

**Note**: These formats may work if you have Calibre installed, but they haven't been tested due to lack of available test files. Most are discontinued/obsolete formats from the 2000s.

### ⚠️ Not Supported: Comic Book Archives
- **CBZ/CBR/CBT/CB7** (.cbz, .cbr, .cbt, .cb7) - Comic book archives
- **Reason**: These are image archives, not text documents
- **Alternative**: Use dedicated comic reader or OCR tool

## Installation Requirements

### Minimal (for basic formats)
```bash
# Just Pandoc
brew install pandoc  # macOS
# or
apt install pandoc   # Linux
```

Supports: EPUB, DOCX, HTML, FB2, ODT, RTF, LaTeX, RST, TXT, MD

### Standard (includes PDF)
```bash
# Pandoc + Poppler (for pdftotext)
brew install pandoc poppler  # macOS
# or
apt install pandoc poppler-utils  # Linux
```

Supports: All minimal formats + PDF

### Full (all formats)
```bash
# Pandoc + Poppler + Calibre
brew install pandoc poppler calibre  # macOS
# or
apt install pandoc poppler-utils calibre  # Linux
```

Supports: All 40+ formats

### Optional: DjVu
```bash
brew install djvulibre  # macOS
# or
apt install djvulibre-bin  # Linux
```

## Format Conversion Methods

allmark uses three conversion strategies:

### 1. Direct Pandoc Conversion
**Formats**: EPUB, DOCX, HTML, FB2, ODT, RTF, LaTeX, RST

**Method**:
```
source_file → Pandoc → markdown → clean
```

**Advantages**:
- Fast
- High quality
- Preserves structure
- No temporary files

### 2. PDF Extraction
**Formats**: PDF

**Method**:
```
PDF → pdftotext (layout mode) → text → clean
  ↓ (if fails)
PDF → pdftotext (raw mode) → text → clean
  ↓ (if fails)
PDF → ebook-convert → HTML → Pandoc → markdown → clean
```

**Advantages**:
- Multiple fallbacks
- Handles various PDF types
- OCR artifact repair

### 3. ebook-convert + Pandoc
**Formats**: MOBI, AZW, LIT, LRF, PDB, PML, PRC, CHM, TCR, XPS, SNB, WOLF, etc.

**Method**:
```
source_file → ebook-convert → HTMLZ → extract → HTML → Pandoc → markdown → clean
```

**Advantages**:
- Handles proprietary formats
- Calibre's extensive format support
- Automatic DRM detection (fails gracefully)

## Format-Specific Notes

### EPUB vs EPUB3
- Both `.epub` and `.epub3` extensions supported
- Pandoc handles EPUB2 and EPUB3 identically
- EPUB3 features (HTML5, enhanced metadata) preserved where possible

### DOC vs DOCX
- `.docx` uses native Pandoc support (faster, better quality)
- `.doc` also works but may require Calibre for very old formats
- Recommend converting old .doc to .docx first if possible

### Kindle Formats (MOBI, AZW, KFX)
- **DRM-protected files will fail** - this is intentional and legal
- Only DRM-free files can be converted
- MOBI format is deprecated by Amazon (use EPUB instead)
- KFX is Amazon's newest format - requires Calibre 5.0+

### PDF Caveats
- **Scanned PDFs**: Text must be OCR'd first (use Adobe Acrobat or OCRmyPDF)
- **Image-based PDFs**: Will extract blank/gibberish text
- **Complex layouts**: Tables and multi-column text may not convert well
- **Best results**: Clean, text-based PDFs with simple layouts

### Comic Books
- **Not supported** for text extraction (they're image archives)
- For text extraction: Use OCR software first
- For reading: Use dedicated comic reader (Calibre viewer, YACReader, etc.)

## Format Quality Matrix

| Format | Quality | Speed | Notes |
|--------|---------|-------|-------|
| EPUB | ⭐⭐⭐⭐⭐ | Fast | Best format, native support |
| DOCX | ⭐⭐⭐⭐⭐ | Fast | Excellent structure preservation |
| HTML | ⭐⭐⭐⭐⭐ | Fast | Direct conversion, very clean |
| FB2 | ⭐⭐⭐⭐ | Fast | Good XML structure |
| PDF | ⭐⭐⭐ | Medium | Depends on PDF quality |
| MOBI | ⭐⭐⭐⭐ | Slow | Via ebook-convert, good quality |
| AZW | ⭐⭐⭐ | Slow | DRM check, variable quality |
| TXT | ⭐⭐⭐⭐ | Instant | No structure, just cleaning |
| ODT | ⭐⭐⭐⭐ | Fast | Good for LibreOffice docs |
| RTF | ⭐⭐⭐ | Fast | Basic formatting preserved |
| LIT | ⭐⭐ | Slow | Old format, limited support |
| PDB | ⭐⭐ | Slow | Very old Palm format |
| DjVu | ⭐⭐⭐ | Medium | Depends on OCR quality |

## Troubleshooting

### Format Not Recognized
```
Error: No files found with supported extensions
```

**Solution**: Check file extension is in supported list. Some formats may need renaming:
```bash
# Example: .azw4 → .azw3
mv book.azw4 book.azw3
```

### ebook-convert Not Found
```
Error: ebook-convert: command not found
```

**Solution**: Install Calibre:
```bash
brew install calibre  # macOS
apt install calibre   # Linux
```

### DRM Protected Files
```
Error: DRM detected
```

**Solution**: allmark cannot convert DRM-protected files. This is intentional and legal:
1. Purchase DRM-free versions
2. Use legitimate DRM removal tools (only for personal backups)
3. Check if format has a DRM-free alternative

### PDF Extraction Failed
```
Error: pdftotext: command not found
```

**Solution**: Install poppler-utils:
```bash
brew install poppler  # macOS
apt install poppler-utils  # Linux
```

### DjVu Not Converting
```
Warning: DjVu format requires djvutxt
```

**Solution**: Install djvulibre:
```bash
brew install djvulibre  # macOS
apt install djvulibre-bin  # Linux
```

## Format Recommendations

### For Distribution
✅ **Use EPUB3** - Universal support, modern features, open standard

### For Archival
✅ **Use PDF/A** - Long-term preservation standard

### For Editing
✅ **Use DOCX or Markdown** - Easy to edit, well-supported

### For Reading on Kindle
✅ **Use MOBI or AZW3** - Native Kindle formats

### Avoid
❌ **Proprietary formats** (LIT, PDB, etc.) - obsolete, poor support
❌ **Comic archives** (CBZ, CBR) - not text documents
❌ **DRM-protected** anything - legal and ethical issues

## Adding New Formats

Want to add support for a new format? Check:

1. **Does Pandoc support it?**
   ```bash
   pandoc --list-input-formats
   ```

2. **Does Calibre support it?**
   ```bash
   ebook-convert --help
   ```

3. If yes to either, open an issue or submit a PR!

## Format Support Summary

| Category | Count | Tool |
|----------|-------|------|
| Pandoc-native | 15 formats | Pandoc |
| ebook-convert | 25+ formats | Calibre |
| Special tools | 1 format | djvutxt |
| Not supported | 4 formats | N/A (comic books) |
| **Total** | **40+ formats** | Mixed |

---

**Last Updated**: Version 0.4.0
**Dependencies**: Pandoc (required), Calibre (optional), poppler-utils (optional), djvulibre (optional)
