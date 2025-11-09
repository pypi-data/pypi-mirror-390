# Allmark Test Suite

Comprehensive test suite for the allmark PDF-to-markdown converter.

## Structure

```
tests/
├── __init__.py              # Package init
├── conftest.py              # Pytest fixtures and configuration
├── test_pdf_extract.py      # PDF extraction tests
├── test_patterns.py         # Pattern detection tests
├── test_cleaners.py         # Cleaning function tests
├── test_converter.py        # Converter/typography tests
├── test_integration.py      # Full pipeline integration tests
├── test_*.py               # Legacy test files (to be migrated)
└── README.md               # This file
```

## Running Tests

### Run all tests:
```bash
cd /path/to/allmark
pytest
```

### Run specific test file:
```bash
pytest tests/test_patterns.py
```

### Run specific test class:
```bash
pytest tests/test_patterns.py::TestTerminalPunctuation
```

### Run specific test:
```bash
pytest tests/test_patterns.py::TestTerminalPunctuation::test_period_is_terminal
```

### Run with verbose output:
```bash
pytest -v
```

### Run with coverage report:
```bash
pytest --cov=src/allmark --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Categories

Tests are organized by module:

### Unit Tests
- `test_pdf_extract.py` - PDF extraction quality scoring
- `test_patterns.py` - Pattern matching and detection
- `test_cleaners.py` - Text cleaning functions
- `test_converter.py` - Typography normalization

### Integration Tests
- `test_integration.py` - Full pipeline scenarios
  - To Kill a Mockingbird style
  - Wittgenstein's Mistress style
  - Where the Red Fern Grows style
  - For Colored Girls play format
  - Edge cases

## Test Coverage

Current test coverage focuses on:

1. **PDF Extraction**
   - Quality scoring system
   - Extraction method selection
   - Text quality analysis

2. **Pattern Detection**
   - Terminal punctuation
   - Dialogue detection
   - Poetry section detection
   - Play/script detection
   - Stage direction detection
   - Character name detection
   - Centered chapter headers
   - Page numbers

3. **Text Cleaning**
   - Frontmatter detection
   - Backmatter detection
   - Paragraph merging
   - Page number removal

4. **Typography**
   - Quote normalization
   - Em-dash normalization
   - ALL CAPS handling
   - Indentation removal

5. **Integration**
   - Complete book processing scenarios
   - Edge case handling
   - Format preservation

## Adding New Tests

When adding new features, add tests in the appropriate file:

1. Create test class: `class TestFeatureName:`
2. Add test methods: `def test_specific_behavior(self):`
3. Use fixtures from `conftest.py` when helpful
4. Run tests to verify: `pytest tests/test_yourfile.py -v`

### Example:
```python
class TestNewFeature:
    """Test new feature description."""

    def test_basic_functionality(self):
        """Test that basic case works."""
        result = my_function("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling."""
        result = my_function("")
        assert result == "default"
```

## Legacy Test Files

The following files are legacy tests from development:
- `test_extraction_debug.py` - Manual extraction debugging
- `test_improvements.py` - Manual improvement testing
- `test_merge.py` - Terminal punctuation checks
- `test_mockingbird.py` - Frontmatter detection example
- `test_where_reasons.py` - Line merging example

These can be migrated into the main test suite or removed.

## Test Requirements

Tests use only Python standard library + pytest:

```bash
pip install pytest pytest-cov
```

## Continuous Integration

To run tests in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=src/allmark --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Contributing

When contributing:
1. Add tests for new features
2. Ensure all tests pass: `pytest`
3. Maintain test coverage: `pytest --cov`
4. Follow existing test patterns
5. Document complex test scenarios

## Test Philosophy

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test complete workflows
- **Fast tests**: Most tests should run in < 1 second
- **Clear assertions**: One logical assertion per test when possible
- **Good names**: Test names describe what they test

## Troubleshooting

### Tests fail with import errors:
```bash
# Make sure you're in the project root
cd /path/to/allmark
pytest
```

### Tests can't find modules:
Check that `conftest.py` properly adds src to path:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

### Want to see print output:
```bash
pytest -s  # Show stdout/stderr
```

### Want to stop on first failure:
```bash
pytest -x  # Exit on first failure
```
