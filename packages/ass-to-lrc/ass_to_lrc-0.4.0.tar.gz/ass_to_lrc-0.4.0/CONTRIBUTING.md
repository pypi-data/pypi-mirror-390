# Contributing Guide

Thank you for contributing to ass-to-lrc! This guide will help you get started.

   This will install the package in editable mode with all dev dependencies.

## Making Changes

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. This leads to more readable
messages that are easy to follow when looking through the project history.

#### Format

```text
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

#### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semi-colons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Changes to build system or dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

#### Scopes

- **cli**: Command-line interface
- **converter**: LRC converter logic
- **parser**: ASS parser logic
- **expander**: LRC expander logic
- **models**: Data models
- **tests**: Test files
- **docs**: Documentation
- **deps**: Dependencies
- **config**: Configuration files

#### Examples

```bash
feat(converter): Add compact LRC format support

Add support for generating compact LRC format where repeated
lyrics share multiple timestamps on a single line.

Closes #123

fix(parser): Handle empty ASS files gracefully

Previously would crash on empty files. Now returns empty lyrics list.

docs(readme): Update installation instructions

test(converter): Add test for compact format with duplicates

chore(deps): Update typer to 0.20.0

ci: Add commitlint workflow for PR validation
```

#### Rules

- Use sentence case for subject (capitalize first letter)
- No period at the end of the subject
- Subject line max 100 characters
- Use imperative mood ("Add feature" not "Added feature")
- Separate subject from body with a blank line
- Wrap body at 72 characters

### Branch Naming

Use descriptive branch names:

- `feat/compact-format`
- `fix/parser-empty-files`
- `docs/update-readme`
- `refactor/converter-logic`

### Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**

   Write code, add tests, update docs as needed.

3. **Run quality checks**

   ```bash
   task qa
   ```

   This runs:
   - Ruff linting
   - Code formatting check
   - Type checking
   - Markdown linting
   - All tests

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat(scope): Add your feature"
   ```

5. **Push to GitHub**

   ```bash
   git push origin feat/your-feature-name
   ```

6. **Create Pull Request**

   - Use a clear, descriptive title (follows conventional commits)
   - Provide detailed description of changes
   - Link related issues
   - Ensure all CI checks pass

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Ruff for linting and formatting

Run formatting:

```bash
task format
```

### Documentation

- Use Markdown for documentation
- Follow markdownlint rules
- Maximum line length: 120 characters

Check markdown:

```bash
task lint-md
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Use `pytest` framework
- Follow naming convention: `test_*.py`
- Use descriptive test names: `test_parser_handles_empty_file()`

### Running Tests

```bash
# Run all tests
task test

# Run with coverage
task test-cov

# Run specific test file
pytest tests/test_parser.py -v

# Run specific test
pytest tests/test_parser.py::test_parse_lyrics -v
```

### Test Coverage

Aim for >80% code coverage. Check coverage with:

```bash
task test-cov-html
```

Then open `htmlcov/index.html` in your browser.

## Code Documentation

### Docstrings

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type hints

Example:

```python
def convert(self, lyrics: list[LyricLine], output_path: Path) -> None:
    """
    Convert lyrics to LRC format and write to file.

    Args:
        lyrics: List of lyric lines to convert
        output_path: Path to write LRC file
    """
```

### Documentation Files

Update relevant documentation when making changes:

- `README.md`: User-facing documentation
- `TESTING.md`: Testing guide
- `PUBLISHING.md`: Publishing guide
- `CONTRIBUTING.md`: This file

## Common Tasks

```bash
# Setup development environment
task dev

# Run all quality checks
task qa

# Run tests
task test

# Run tests with coverage
task test-cov

# Lint code
task lint

# Auto-fix linting issues
task lint-fix

# Format code
task format

# Type check
task typecheck

# Lint markdown
task lint-md

# Build package
task build

# Clean generated files
task clean

# Show all available tasks
task --list
```

## Getting Help

- **Issues**: <https://github.com/nattadasu/ass-to-lrc/issues>
- **Discussions**: <https://github.com/nattadasu/ass-to-lrc/discussions>

## Code of Conduct

Be respectful and inclusive. We're all here to learn and build something great together.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Pre-commit Hook Performance

### Speed Optimizations

The project is configured for fast pre-commit hooks:

- **Local tools**: mypy and markdownlint run as local system commands (faster than downloading)
- **Ruff**: Extremely fast linter/formatter written in Rust
- **Minimal hooks**: Only essential checks enabled

### Skip Hooks (when needed)

```bash
# Skip all hooks
git commit --no-verify -m "message"

# Skip specific hook
SKIP=mypy git commit -m "message"

# Skip multiple hooks
SKIP=mypy,markdownlint git commit -m "message"
```

### Run Hooks Manually

```bash
# Run on all files
task pre-commit

# Run on staged files only
uv run pre-commit run

# Run specific hook
uv run pre-commit run mypy

# Run on specific files
uv run pre-commit run --files file1.py file2.py
```

### Performance Tips

1. **Stage changes incrementally**: Smaller diffs = faster hooks
2. **Use local system tools**: Already configured for mypy and markdownlint
3. **Skip when iterating**: Use `--no-verify` during rapid development
4. **Update pre-commit**: `task pre-commit-update` for latest optimizations
