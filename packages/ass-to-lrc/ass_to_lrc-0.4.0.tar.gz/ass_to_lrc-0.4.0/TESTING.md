# Testing Guide

This document describes the testing infrastructure for ass2lrc.

## Test Structure

The test suite is organized into the following modules:

### `test_parser.py` - ASS Parser Tests

Tests for parsing ASS subtitle files and extracting metadata/lyrics.

**Coverage:**

- Parser initialization
- Metadata extraction from Comment events
- Metadata extraction from effect=tag
- Lyric parsing with karaoke tags
- Plain text parsing
- Time-based sorting
- Comment event filtering

### `test_converter.py` - LRC Converter Tests

Tests for converting parsed lyrics to various LRC formats.

**Coverage:**

- Timestamp formatting (standard and inline)
- Metadata tag generation
- Enhanced LRC with word timing
- Simple LRC without word timing
- Compact format with repeated lyrics
- Line gap generation
- Empty lyrics handling
- No word timing at line end

### `test_expander.py` - LRC Expander Tests

Tests for expanding compact LRC to standard format.

**Coverage:**

- Timestamp extraction
- Single and multiple timestamp handling
- Compact to standard expansion
- Already standard format handling
- Sorted output verification
- Empty file handling
- Metadata-only files

### `test_integration.py` - Integration Tests

End-to-end tests for complete workflows.

**Coverage:**

- Full enhanced LRC workflow
- Full simple LRC workflow
- Compact → Expand workflow
- Metadata preservation
- Multiple format conversions

## Running Tests

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py -v

# Run specific test
pytest tests/test_parser.py::test_parse_lyrics -v
```

### With Coverage

```bash
# Install coverage
pip install pytest-cov

# Run with coverage report
pytest tests/ --cov=ass2lrc --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=ass2lrc --cov-report=html
```

### Using Make

```bash
# Run tests
make test

# Run with coverage
make test-cov

# Run all quality checks
make all
```

### Using Test Runner Script

```bash
# Run all checks (lint, format, typecheck, test)
python run_tests.py
```

## Test Fixtures

The test suite uses pytest fixtures to create temporary test files:

- `sample_ass_file`: Complete ASS file with Comment metadata
- `tag_effect_ass_file`: ASS file with effect=tag metadata
- `sample_metadata`: Sample Metadata object
- `sample_lyrics`: Sample LyricLine list with syllables
- `compact_lrc_file`: Compact format LRC file
- `simple_lrc_file`: Standard format LRC file
- `full_ass_file`: Complete ASS file for integration tests

## CI/CD

Tests run automatically on GitHub Actions for:

- Python 3.11, 3.12, 3.13
- Every push to main/master
- Every pull request

See `.github/workflows/test.yml` for configuration.

## Writing New Tests

When adding new features, follow these guidelines:

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test complete workflows
3. **Use Fixtures**: Create reusable test data with pytest fixtures
4. **Test Edge Cases**: Empty inputs, invalid data, boundary conditions
5. **Descriptive Names**: Test function names should describe what they test

Example:

```python
def test_parse_empty_ass_file(tmp_path: Path) -> None:
    """Test parsing an empty ASS file."""
    empty_file = tmp_path / "empty.ass"
    empty_file.write_text("", encoding="utf-8")
    
    parser = ASSParser(empty_file)
    lyrics = parser.parse_lyrics()
    
    assert len(lyrics) == 0
```

## Test Statistics

Current test coverage:

- **Total Tests**: 29
- **Parser Tests**: 8
- **Converter Tests**: 9
- **Expander Tests**: 6
- **Integration Tests**: 5
- **Status**: ✅ All passing
