"""allmark - Universal eBook → Markdown converter and cleaner."""

__version__ = "0.4.0"

from .converter import convert_file, find_files, clean_markdown
from .cli import main

__all__ = ['convert_file', 'find_files', 'clean_markdown', 'main']
