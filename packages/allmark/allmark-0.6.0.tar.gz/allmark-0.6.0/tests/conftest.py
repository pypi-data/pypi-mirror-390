"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os

# Add src to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_text_simple():
    """Simple text sample for basic tests."""
    return "This is a simple test sentence. It has multiple sentences."


@pytest.fixture
def sample_text_with_frontmatter():
    """Text sample with frontmatter."""
    return """Copyright 2020
Dedication

Chapter 1

Once upon a time, there was a story."""


@pytest.fixture
def sample_text_with_poetry():
    """Text sample containing poetry."""
    return """Regular paragraph.

In the beginning
was the word
and the word
was poetry

Regular paragraph again."""


@pytest.fixture
def sample_text_with_dialogue():
    """Text sample containing dialogue."""
    return '''The sun was shining.
"Hello," she said.
"How are you?" he replied.
They walked together.'''


@pytest.fixture
def sample_text_with_play():
    """Text sample in play format."""
    return """HAMLET
To be, or not to be, that is the question.

(aside)
Whether 'tis nobler in the mind to suffer.

OPHELIA
My lord, I have remembrances of yours."""


@pytest.fixture
def sample_text_all_caps():
    """Text with ALL CAPS words."""
    return "WHEN HE was young, he lived in a HOUSE near the OCEAN."


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path
