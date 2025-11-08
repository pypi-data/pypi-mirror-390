"""Utility functions."""

from . import patterns


def roman_to_int(s):
    """Convert Roman numeral to integer."""
    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100,
              'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}
    total = 0
    prev = 0
    for c in reversed(s):
        val = values.get(c, 0)
        if val < prev:
            total -= val
        else:
            total += val
        prev = val
    return total


def looks_like_code(line):
    """Detect if line looks like code/markup rather than prose."""
    return patterns.is_code_like(line)


def looks_like_junk(line):
    """Enhanced junk detection."""
    stripped = line.strip()
    if not stripped:
        return False

    # Check if it's code first
    if looks_like_code(line):
        return True

    return patterns.is_junk(stripped)
