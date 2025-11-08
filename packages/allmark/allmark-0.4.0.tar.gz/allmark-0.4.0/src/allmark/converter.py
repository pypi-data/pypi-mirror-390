"""File conversion and processing."""

import os
import subprocess
import sqlite3
import time
import json

from . import patterns
from .ocr import repair_ocr_artifacts
from .cleaners import (
    detect_repeating_headers_footers,
    detect_and_remove_code_blocks,
    validate_and_fix_formatting,
    remove_toc_clusters,
    remove_tables,
    remove_index_section,
    remove_page_numbers,
    aggressive_artifact_removal,
    find_content_start,
    merge_broken_paragraphs,
    find_backmatter_start,
    standardize_chapters,
)
from .analyzers import analyze_document_structure
from .tokenizer import text_to_jsonl_records, count_tokens
from .pdf_extract import extract_pdf_text


def create_jsonl(markdown_path, jsonl_path, token_size, strict_split=False, source_file=None, custom_metadata=None):
    """
    Convert markdown file to JSONL with token-based chunking.

    Args:
        markdown_path: Path to markdown file
        jsonl_path: Path to output JSONL file
        token_size: Maximum tokens per chunk
        strict_split: If True, split strictly. If False, respect paragraphs.
        source_file: Source filename for metadata
        custom_metadata: Dict of custom metadata to include in each record
    """
    # Read markdown
    with open(markdown_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Create JSONL records
    metadata = {
        'markdown_file': os.path.basename(markdown_path),
        'split_mode': 'strict' if strict_split else 'paragraph_aware'
    }

    # Add custom metadata if provided
    if custom_metadata:
        metadata.update(custom_metadata)

    records = text_to_jsonl_records(
        text=text,
        max_tokens=token_size,
        strict=strict_split,
        source_file=source_file,
        metadata=metadata
    )

    # Write JSONL
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    total_tokens = sum(r['token_count'] for r in records)
    print(f"    → {len(records)} chunks, ~{total_tokens:,} tokens")


def run_command(cmd):
    """Execute shell command with Calibre binaries in PATH."""
    try:
        start = time.time()

        # Add Calibre binaries to PATH (macOS Homebrew installation)
        env = os.environ.copy()
        calibre_path = "/opt/homebrew/Caskroom/calibre/8.13.0/calibre.app/Contents/MacOS"
        if os.path.exists(calibre_path):
            env['PATH'] = f"{calibre_path}:{env.get('PATH', '')}"

        # Also check for standard Calibre installation paths
        alt_paths = [
            "/Applications/calibre.app/Contents/MacOS",  # macOS standard install
            "/usr/bin",  # Linux apt install
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                env['PATH'] = f"{alt_path}:{env.get('PATH', '')}"

        subprocess.run(cmd, shell=True, check=True, capture_output=True, env=env)
        return True, time.time() - start
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}\n{e.stderr.decode(errors='ignore')}")
        return False, 0


def clean_markdown(path, strip=True):
    """Complete cleaning pipeline with statistical analysis."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    original_len = len(text)

    if not strip:
        # Skip cleaning, just return word count
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return len(text.split()), "none"

    # Stage 1: Repair OCR artifacts (soft hyphens, ligatures, broken hyphenation)
    text = repair_ocr_artifacts(text)

    # Stage 2: Remove all artifacts
    text = aggressive_artifact_removal(text)

    # Stage 3: Detect and remove code blocks
    text = detect_and_remove_code_blocks(text)

    # Stage 4: Detect and remove repeating headers/footers
    text = detect_repeating_headers_footers(text)

    # Stage 5: Remove page numbers
    text = remove_page_numbers(text)

    # Stage 6: Remove TOC clusters
    text = remove_toc_clusters(text)

    # Stage 6.5: Remove tables (metadata artifacts)
    text = remove_tables(text)

    # Stage 7: Analyze document structure for intelligent trimming
    analysis = analyze_document_structure(text)

    # Stage 8: Find and remove frontmatter using analysis
    start_idx = find_content_start(text)
    if start_idx > 0:
        lines = text.split('\n')
        text = '\n'.join(lines[start_idx:])

    # Stage 9: Remove backmatter using analysis
    backmatter_idx = find_backmatter_start(text)
    if backmatter_idx:
        lines = text.split('\n')
        text = '\n'.join(lines[:backmatter_idx])

    # Stage 9.5: Remove index section (if present)
    text = remove_index_section(text)

    # Stage 10: Standardize chapter headers (where they exist)
    text = standardize_chapters(text)

    # Stage 11: Typography normalization
    text = text.replace(""", '"').replace(""", '"')
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace("--", "--")
    text = text.replace("…", "...")

    # Stage 12: Validate and fix markdown formatting
    text = validate_and_fix_formatting(text)

    # Stage 13: Fix spacing around headers
    text = patterns.HEADER_BEFORE.sub(r'\n\n\1', text)
    text = patterns.HEADER_AFTER.sub(r'\1\n\n\2', text)

    # Stage 14: Collapse excessive whitespace
    text = patterns.EXCESSIVE_NEWLINES.sub('\n\n\n', text)
    text = patterns.TRAILING_WHITESPACE.sub('', text)

    # Stage 15: Remove artifact-only lines (but preserve valid elements)
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append(line)
            continue

        # Whitelist: valid scene breaks and separators
        if stripped in ('***', '---', '* * *', '- - -', '…'):
            cleaned.append(line)
            continue

        # Whitelist: ellipsis variations
        if stripped in ('...', '. . .', '…'):
            cleaned.append(line)
            continue

        # Remove artifact-only lines
        if not patterns.ARTIFACT_LINE.match(stripped):
            cleaned.append(line)
    text = '\n'.join(cleaned)

    # Stage 16: Merge broken paragraphs (dialogue-aware)
    text = merge_broken_paragraphs(text)

    # Stage 17: Remove standalone title markers like "_TITLE_"
    text = patterns.TITLE_MARKER.sub('', text)

    # Final cleanup
    text = text.lstrip().rstrip() + '\n'

    # SAFETY CHECK: Don't save if we removed more than 50%
    cleaned_len = len(text)
    removed_pct = ((original_len - cleaned_len) / original_len * 100) if original_len > 0 else 0

    if removed_pct > 50:
        print(f"  WARNING: Would remove {removed_pct:.1f}% - TOO MUCH, keeping original!")
        return 0, "skipped"

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    strategy = "comprehensive"
    if removed_pct > 5:
        strategy = "aggressive"
    elif removed_pct > 1:
        strategy = "moderate"
    else:
        strategy = "light"

    return len(text.split()), strategy


def find_files(directory, extensions=None):
    """Recursively find all files with supported ebook formats."""
    if extensions is None:
        extensions = {
            # Pandoc-supported formats
            ".epub", ".epub3", ".docx", ".doc", ".html", ".htm", ".xhtml",
            ".fb2", ".latex", ".tex", ".rst", ".odt", ".ott", ".rtf",
            ".txt", ".text", ".md",
            # PDF
            ".pdf",
            # Kindle formats (require ebook-convert)
            ".mobi", ".azw", ".azw3", ".azw4", ".kfx", ".kf8", ".kpf",
            # Other reader formats (require ebook-convert)
            ".lit", ".lrf", ".lrx",  # Microsoft Reader, Sony Reader
            ".pdb", ".pml", ".pmlz", ".prc",  # Palm, Plucker
            ".rb", ".rbz",  # RocketBook
            ".tcr", ".tr2", ".tr3",  # TomeRaider
            ".oxps", ".xps",  # OpenXPS
            ".snb", ".wolf",  # Shanda Bambook, Hanlin
            ".chm", ".inf",  # Compiled HTML Help
            # Special formats
            ".djvu",  # DjVu (requires djvutxt)
            ".cbz", ".cbr", ".cbt", ".cb7",  # Comic books (not supported)
        }

    found = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                found.append(os.path.join(root, file))
    return found


def convert_file(file, src_dir, out_dir, db_conn, force_reconvert=True, clean_existing_md=True, strip=True,
                 jsonl=False, token_size=None, strict_split=False, custom_metadata=None):
    """Convert ebook to markdown and optionally to JSONL.

    Args:
        file: Path to input file
        src_dir: Source directory
        out_dir: Output directory
        db_conn: Database connection
        force_reconvert: Force reconversion of existing files
        clean_existing_md: Clean existing markdown files
        strip: Strip frontmatter/backmatter
        jsonl: Also create JSONL output
        token_size: Token size for JSONL chunks (required if jsonl=True)
        strict_split: If True, split strictly at token boundaries. If False, respect paragraphs.
        custom_metadata: Dict of custom metadata to add to JSONL records
    """
    ext = file.split(".")[-1].lower()
    rel_path = os.path.relpath(file, src_dir)
    name = os.path.splitext(rel_path)[0]
    out = os.path.join(out_dir, f"{name}.md")

    os.makedirs(os.path.dirname(out), exist_ok=True)

    cur = db_conn.cursor()

    # If already markdown, just clean
    if ext == "md":
        if clean_existing_md:
            print(f"🧹 {os.path.basename(file)}")
            start = time.time()
            wc, strategy = clean_markdown(file, strip=strip)
            duration = time.time() - start

            if wc > 0:
                print(f"  ✅ {wc:,} words ({strategy})")

                # Create JSONL if requested
                if jsonl and token_size:
                    jsonl_out = os.path.join(out_dir, f"{name}.jsonl")
                    create_jsonl(file, jsonl_out, token_size, strict_split,
                                source_file=os.path.basename(file), custom_metadata=custom_metadata)
                    print(f"  📄 JSONL created: {os.path.basename(jsonl_out)}")

                cur.execute(
                    "INSERT INTO conversions (source_file, output_file, extension, word_count, size_kb, duration_s, status, cleaning_strategy) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (file, file, ext, wc, os.path.getsize(file)/1024, duration, "cleaned", strategy),
                )
                db_conn.commit()
        return

    if os.path.exists(out) and not force_reconvert:
        return

    print(f"🔄 {os.path.basename(file)}")
    ok = False
    duration = 0

    # Pandoc-supported formats (direct conversion)
    if ext in ("epub", "epub3"):
        ok, duration = run_command(f'pandoc "{file}" -f epub -t markdown --wrap=none --strip-comments --markdown-headings=atx -o "{out}"')
    elif ext in ("docx", "doc"):
        ok, duration = run_command(f'pandoc "{file}" -t markdown --wrap=none -o "{out}"')
    elif ext in ("html", "htm", "xhtml"):
        ok, duration = run_command(f'pandoc "{file}" -f html -t markdown --wrap=none -o "{out}"')
    elif ext == "fb2":
        # FictionBook 2.0 - Try pandoc first, fallback to ebook-convert
        ok, duration = run_command(f'pandoc "{file}" -f fb2 -t markdown --wrap=none -o "{out}"')
        if not ok:
            # Fallback to ebook-convert (some FB2 files may be invalid XML)
            tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
            tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
            ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
            if ok and os.path.exists(tmp_htmlz):
                run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
                ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
                for f in (tmp_html, tmp_htmlz):
                    if os.path.exists(f):
                        os.remove(f)
    elif ext in ("latex", "tex"):
        ok, duration = run_command(f'pandoc "{file}" -f latex -t markdown --wrap=none -o "{out}"')
    elif ext == "rst":
        ok, duration = run_command(f'pandoc "{file}" -f rst -t markdown --wrap=none -o "{out}"')
    elif ext in ("odt", "ott"):
        # OpenDocument Text
        ok, duration = run_command(f'pandoc "{file}" -f odt -t markdown --wrap=none -o "{out}"')
    elif ext == "rtf":
        # Rich Text Format
        ok, duration = run_command(f'pandoc "{file}" -f rtf -t markdown --wrap=none -o "{out}"')
    elif ext in ("txt", "text"):
        # Plain text - just copy and clean
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        with open(out, 'w', encoding='utf-8') as f:
            f.write(text)
        ok = True
        duration = 0
    elif ext == "pdf":
        # PDF conversion: try pdftotext -> ebook-convert fallback
        ok, duration, method = extract_pdf_text(file, out)

        if ok and os.path.exists(out) and os.path.getsize(out) >= 100:
            # Success with pdftotext
            pass
        else:
            # Fallback to ebook-convert
            tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
            tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
            ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
            if ok and os.path.exists(tmp_htmlz):
                run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
                ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
                for f in (tmp_html, tmp_htmlz):
                    if os.path.exists(f):
                        os.remove(f)
                method = "ebook-convert"
    elif ext in ("mobi", "azw", "azw3", "azw4", "kfx", "kf8", "kpf"):
        # Kindle formats - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("lit", "lrf", "lrx"):
        # Microsoft Reader (.lit), Sony Reader (.lrf, .lrx) - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("pdb", "pml", "pmlz", "prc"):
        # Palm formats (.pdb, .pml), Plucker (.prc) - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("cbz", "cbr", "cbt", "cb7"):
        # Comic book archives - extract images only (no text conversion)
        print(f"  ⚠️  Comic book format ({ext}) - image extraction not supported")
        print(f"      Use dedicated comic reader or OCR tool")
        ok = False
    elif ext == "djvu":
        # DjVu - requires djvutxt tool
        ok, duration = run_command(f'djvutxt "{file}" "{out}"')
        if not ok:
            print(f"  ⚠️  DjVu format requires djvutxt (install djvulibre)")
    elif ext in ("chm", "inf"):
        # Compiled HTML Help - requires ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("rb", "rbz"):
        # RocketBook - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("tcr", "tr2", "tr3"):
        # TomeRaider - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("oxps", "xps"):
        # OpenXPS/XPS - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)
    elif ext in ("snb", "wolf"):
        # Shanda Bambook (.snb), Hanlin eReader (.wolf) - require ebook-convert
        tmp_htmlz = os.path.join(out_dir, f"{os.path.basename(name)}.htmlz")
        tmp_html = os.path.join(out_dir, f"{os.path.basename(name)}.html")
        ok, duration = run_command(f'ebook-convert "{file}" "{tmp_htmlz}"')
        if ok and os.path.exists(tmp_htmlz):
            run_command(f'unzip -p "{tmp_htmlz}" index.html > "{tmp_html}"')
            ok, _ = run_command(f'pandoc "{tmp_html}" -t markdown -o "{out}"')
            for f in (tmp_html, tmp_htmlz):
                if os.path.exists(f):
                    os.remove(f)

    if ok and os.path.exists(out):
        wc, strategy = clean_markdown(out, strip=strip)
        if wc > 0:
            print(f"  ✅ {wc:,} words ({strategy})")

            # Create JSONL if requested
            if jsonl and token_size:
                jsonl_out = os.path.join(out_dir, f"{name}.jsonl")
                create_jsonl(out, jsonl_out, token_size, strict_split,
                            source_file=os.path.basename(file), custom_metadata=custom_metadata)
                print(f"  📄 JSONL created: {os.path.basename(jsonl_out)}")

            cur.execute(
                "INSERT INTO conversions (source_file, output_file, extension, word_count, size_kb, duration_s, status, cleaning_strategy) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (file, out, ext, wc, os.path.getsize(file)/1024, duration, "success", strategy),
            )
            db_conn.commit()
