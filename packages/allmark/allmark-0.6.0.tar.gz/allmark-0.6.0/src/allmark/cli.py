"""Command-line interface for allmark."""

import argparse
import os
import sqlite3
import sys
import json

from .converter import find_files, convert_file


def setup_database(db_path):
    """Initialize the conversion tracking database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS conversions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file TEXT,
        output_file TEXT,
        extension TEXT,
        word_count INTEGER,
        size_kb REAL,
        duration_s REAL,
        status TEXT,
        cleaning_strategy TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    return conn


def print_help():
    """Print user-friendly help message."""
    help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                   allmark                                    ║
║              Universal eBook → Markdown Converter & Cleaner                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

USAGE:
    allmark --in <directory> [OPTIONS]

REQUIRED:
    --in, --input <dir>      Input directory containing ebook files

                             Verified formats (tested & working):
                             • EPUB (.epub, .epub3)
                             • Microsoft Word (.docx)
                             • PDF (.pdf) - requires pdftotext
                             • HTML (.html, .htm, .xhtml)
                             • Plain text (.txt, .text, .md)
                             • OpenDocument (.odt)
                             • Rich Text (.rtf)
                             • LaTeX (.tex, .latex)
                             • reStructuredText (.rst)

                             Additional formats (requires Calibre):
                             • Kindle (.mobi, .azw, .azw3, .kfx, .kf8)
                             • FictionBook (.fb2)
                             • DjVu (.djvu) - requires djvutxt
                             • 25+ legacy formats (.lit, .lrf, .pdb, etc.)

OPTIONAL:
    --out, --output <dir>    Output directory for markdown files
                             (default: same as input directory)

    --no-strip               Convert WITHOUT cleaning:
                             • Keeps frontmatter (copyright, dedications)
                             • Keeps backmatter (author bio, ads)
                             • Keeps headers/footers and page numbers
                             • Keeps all artifacts and metadata

    --force                  Force reconversion of existing files

    --no-clean-md            Skip cleaning existing .md files

    --db <path>              Conversion log database path
                             (default: ./conversion_log.db)

    --jsonl                  Also create JSONL output with token-based chunking

    --token-size <n>         Maximum tokens per JSONL chunk
                             (default: 512)

    --strict-split           Split strictly at token boundaries
                             (default: respect paragraph boundaries)

    --metadata <file>        JSON file with custom metadata for JSONL records
                             Example: {"genre": "fiction", "language": "en"}

EXAMPLES:
    # Convert all ebooks in a directory (with cleaning)
    allmark --in ./my-books

    # Convert to different directory
    allmark --in ./ebooks --out ./markdown

    # Convert without stripping content
    allmark --in ./books --no-strip

    # Force reconversion of all files
    allmark --in ./books --force

    # Convert to markdown + JSONL with 1024 token chunks
    allmark --in ./books --jsonl --token-size 1024

    # JSONL with strict splitting (ignores paragraphs)
    allmark --in ./books --jsonl --strict-split

    # JSONL with custom metadata
    allmark --in ./books --jsonl --metadata ./book_metadata.json

WHAT GETS CLEANED:
    ✓ OCR artifacts (broken hyphens, ligatures)
    ✓ Frontmatter (title pages, copyright, TOC)
    ✓ Backmatter (author bios, ads, previews)
    ✓ Headers and footers
    ✓ Page numbers
    ✓ eBook metadata and CSS artifacts
    ✓ Broken paragraphs rejoined intelligently

For more info: https://github.com/dcondrey/allmark
"""
    print(help_text)


def main():
    """Main entry point for the CLI."""
    # Show friendly help if no arguments or just --help
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description='Universal eBook → Markdown converter and cleaner',
        prog='allmark',
        add_help=False  # We'll handle help ourselves
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show this help message'
    )
    parser.add_argument(
        '--in', '--input',
        dest='input_dir',
        required=False,
        help='Input directory containing ebook files'
    )
    parser.add_argument(
        '--out', '--output',
        dest='output_dir',
        default=None,
        help='Output directory for converted markdown files (default: same as --in)'
    )
    parser.add_argument(
        '--no-strip',
        dest='no_strip',
        action='store_true',
        help='Convert files without stripping frontmatter/backmatter or cleaning content'
    )
    parser.add_argument(
        '--db',
        dest='db_path',
        default='./conversion_log.db',
        help='Path to conversion log database (default: ./conversion_log.db)'
    )
    parser.add_argument(
        '--force',
        dest='force',
        action='store_true',
        help='Force reconversion of files that already exist'
    )
    parser.add_argument(
        '--no-clean-md',
        dest='no_clean_md',
        action='store_true',
        help='Skip cleaning existing markdown files'
    )
    parser.add_argument(
        '--jsonl',
        dest='jsonl',
        action='store_true',
        help='Also create JSONL output with token-based chunking'
    )
    parser.add_argument(
        '--token-size',
        dest='token_size',
        type=int,
        default=512,
        help='Maximum tokens per JSONL chunk (default: 512)'
    )
    parser.add_argument(
        '--strict-split',
        dest='strict_split',
        action='store_true',
        help='Split strictly at token boundaries (default: respect paragraph boundaries)'
    )
    parser.add_argument(
        '--metadata',
        dest='metadata_file',
        default=None,
        help='JSON file with custom metadata to add to JSONL records'
    )

    args = parser.parse_args()

    # Handle help flag
    if args.help:
        print_help()
        sys.exit(0)

    # Validate required argument
    if not args.input_dir:
        print("ERROR: --in <directory> is required\n")
        print_help()
        sys.exit(1)

    src_dir = args.input_dir

    # Validate input directory exists
    if not os.path.exists(src_dir):
        print(f"ERROR: Input directory does not exist: {src_dir}")
        sys.exit(1)

    if not os.path.isdir(src_dir):
        print(f"ERROR: Input path is not a directory: {src_dir}")
        sys.exit(1)

    # Use input dir as output dir if not specified
    out_dir = args.output_dir if args.output_dir else src_dir
    db_path = args.db_path
    force_reconvert = args.force
    clean_existing_md = not args.no_clean_md
    strip = not args.no_strip
    jsonl = args.jsonl
    token_size = args.token_size
    strict_split = args.strict_split

    # Load custom metadata if provided
    custom_metadata = None
    if args.metadata_file:
        if not os.path.exists(args.metadata_file):
            print(f"ERROR: Metadata file not found: {args.metadata_file}")
            sys.exit(1)

        try:
            with open(args.metadata_file, 'r') as f:
                custom_metadata = json.load(f)

            if not isinstance(custom_metadata, dict):
                print("ERROR: Metadata file must contain a JSON object (dict)")
                sys.exit(1)

            print(f"📋 Loaded custom metadata: {list(custom_metadata.keys())}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in metadata file: {e}")
            sys.exit(1)

    # Validate JSONL options
    if strict_split and not jsonl:
        print("WARNING: --strict-split has no effect without --jsonl")

    if args.metadata_file and not jsonl:
        print("WARNING: --metadata has no effect without --jsonl")

    if jsonl and token_size < 1:
        print("ERROR: --token-size must be positive")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(out_dir, exist_ok=True)

    # Setup database
    conn = setup_database(db_path)

    print(f"📂 Scanning {src_dir}...\n")

    # Use all supported formats (find_files default)
    ebook_files = find_files(src_dir)
    md_files = find_files(src_dir, {".md"}) if clean_existing_md else []

    # Remove .md files from ebook_files to avoid duplication
    ebook_files = [f for f in ebook_files if not f.endswith('.md')]

    total = len(ebook_files) + len(md_files)
    if total == 0:
        print("No files found.")
        return

    strip_mode = "no-strip" if not strip else "strip"
    output_format = f"MD+JSONL (tokens={token_size}, {'strict' if strict_split else 'paragraph-aware'})" if jsonl else "Markdown"
    print(f"📚 Processing {total} files")
    print(f"   Mode: {strip_mode}, Format: {output_format}\n")

    for i, file in enumerate(ebook_files, 1):
        print(f"[{i}/{total}] ", end="")
        convert_file(file, src_dir, out_dir, conn, force_reconvert, clean_existing_md, strip,
                     jsonl=jsonl, token_size=token_size, strict_split=strict_split,
                     custom_metadata=custom_metadata)

    for i, file in enumerate(md_files, len(ebook_files) + 1):
        print(f"[{i}/{total}] ", end="")
        convert_file(file, src_dir, out_dir, conn, force_reconvert, clean_existing_md, strip,
                     jsonl=jsonl, token_size=token_size, strict_split=strict_split,
                     custom_metadata=custom_metadata)

    print("\n" + "="*60)
    print("✅ All files processed!")
    print(f"📊 Log: {db_path}")
    print("="*60)
    conn.close()


if __name__ == "__main__":
    main()
