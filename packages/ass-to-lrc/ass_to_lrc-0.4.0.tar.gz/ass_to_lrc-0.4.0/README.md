# ASS to LRC Converter

A Pythonic CLI application to convert ASS (Advanced SubStation Alpha) subtitle files to LRC (Lyrics) format with support
for enhanced word-level timing.

## Features

- **OOP Design**: Clean, maintainable object-oriented architecture with dedicated classes for parsing, conversion, and
  data models
- **Bidirectional Conversion**: Convert between ASS and LRC formats
- **Enhanced LRC**: Generates `.elrc` files with word-level timing from `\K` karaoke tags
- **Simple LRC**: Standard LRC format without word timing
- **Compact Format**: Merge repeated lyrics with multiple timestamps (e.g., choruses)
- **Expand Command**: Convert compact LRC back to standard sorted format
- **LRC to ASS**: Convert LRC files back to ASS format with karaoke timing support
- **Metadata Support**: Automatically extracts and converts metadata tags (artist, lyricist, album, etc.)
- **Comment Events**: Support both ASS Comment events and effect=tag for metadata
- **Effect-Based Line Breaks**: Automatically add line breaks when effect contains "break"
- **Configurable Gaps**: Add customizable gaps between lyric lines
- **Typer CLI**: Modern, user-friendly command-line interface with subcommands

## Installation

```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
# Convert ASS to enhanced LRC (default)
ass2lrc convert input.ass

# Outputs: input.elrc
```

### Commands

#### `convert` - Convert ASS to LRC

Convert ASS subtitle files to LRC lyrics format.

```bash
ass2lrc convert [OPTIONS] INPUT_FILE
```

**Arguments:**

- `INPUT_FILE` - Path to input ASS file (required)

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output LRC file path | Same as input with `.lrc`/`.elrc` extension |
| `--enhanced` | `-e` | Generate enhanced LRC with word timing | `enabled` |
| `--simple` | `-s` | Generate simple LRC (line timing only) | `disabled` |
| `--compact` | `-c` | Use compact format (multiple timestamps per line) | `disabled` |
| `--gap` | `-g` | Gap in seconds between lines (≥0.0) | `1.0` |
| `--version` | `-v` | Show version and exit | - |
| `--help` | | Show help message | - |

**Examples:**

```bash
# Convert to enhanced LRC (default)
ass2lrc convert song.ass

# Convert to simple LRC
ass2lrc convert song.ass --simple

# Specify output file
ass2lrc convert song.ass -o lyrics.lrc

# Custom line gap (0.5 seconds)
ass2lrc convert song.ass --gap 0.5

# Compact format for repeated lyrics
ass2lrc convert song.ass --compact

# Enhanced LRC with custom gap
ass2lrc convert song.ass -e -g 0.8 -o song.elrc

# Simple LRC with no gap
ass2lrc convert song.ass -s -g 0
```

#### `expand` - Expand Compact LRC

Expand compact LRC format to standard sorted format.

```bash
ass2lrc expand [OPTIONS] INPUT_FILE
```

**Arguments:**

- `INPUT_FILE` - Path to input compact LRC file (required)

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output expanded LRC file path | Input with `_expanded` suffix |
| `--help` | | Show help message | - |

**Examples:**

```bash
# Expand compact LRC to standard format
ass2lrc expand compact.lrc

# Specify output file
ass2lrc expand compact.lrc -o expanded.lrc
```

#### `lrc2ass` - Convert LRC to ASS

Convert LRC lyrics files back to ASS subtitle format.

```bash
ass2lrc lrc2ass [OPTIONS] INPUT_FILE
```

**Arguments:**

- `INPUT_FILE` - Path to input LRC file (required)

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output ASS file path | Same as input with `.ass` extension |
| `--karaoke` | `-k` | Generate karaoke timing tags from enhanced LRC | `enabled` |
| `--no-karaoke` | `-K` | Disable karaoke tags (plain text only) | `disabled` |
| `--help` | | Show help message | - |

**Examples:**

```bash
# Convert enhanced LRC to ASS with karaoke tags
ass2lrc lrc2ass song.elrc

# Convert simple LRC to ASS without karaoke
ass2lrc lrc2ass song.lrc --no-karaoke

# Specify output file
ass2lrc lrc2ass lyrics.lrc -o subtitles.ass
```

### Global Options

```bash
# Show version
ass2lrc --version

# Show help
ass2lrc --help

# Show help for specific command
ass2lrc convert --help
ass2lrc expand --help
ass2lrc lrc2ass --help
```

## ASS Format Requirements

### Metadata Tags

Include metadata using Comment events or Dialogue lines with `effect=tag`:

#### Method 1: Comment events (recommended)

```ass
Comment: 0,0:00:00.00,0:00:00.00,Default,ti,0,0,0,,Song Title
Comment: 0,0:00:00.00,0:00:00.00,Default,ar,0,0,0,,Artist Name
Comment: 0,0:00:00.00,0:00:00.00,Default,lr,0,0,0,,Lyricist Name
```

#### Method 2: Dialogue with effect=tag

```ass
Dialogue: 0,0:00:00.00,0:00:02.00,Default,ti,0,0,0,tag,Song Title
Dialogue: 0,0:00:00.00,0:00:02.00,Default,ar,0,0,0,tag,Artist Name
Dialogue: 0,0:00:00.00,0:00:02.00,Default,lr,0,0,0,tag,Lyricist Name
```

Supported metadata tags (following LRC specification):

- `ti`: Title of the song
- `ar`: Artist performing the song
- `al`: Album the song is from
- `au`: Author of the song
- `lr`: Lyricist of the song
- `length`: Length of the song (mm:ss)
- `by`: Author of the LRC file (not the song)
- `offset`: Global offset value for lyric times in milliseconds (e.g., +100 or -50)
- `re` / `tool`: The player or editor that created the LRC file
- `ve`: The version of the program
- `#`: Comments (can have multiple)

### Karaoke Timing

Use `\K` or `\k` tags for syllable timing (in centiseconds):

```ass
Dialogue: 0,0:00:00.62,0:00:07.52,Default,,0,0,0,,{\K72}Text{\K106}Here
```

### Effect-Based Line Breaks

Lines with an effect field containing "break" (case-insensitive) will automatically add an empty line after them in the LRC output:

```ass
Dialogue: 0,0:00:10.00,0:00:12.00,Default,,0,0,0,linebreak,First verse
Dialogue: 0,0:00:13.00,0:00:15.00,Default,,0,0,0,,Second verse
```

This will produce:

```lrc
[00:10.00]First verse
[00:12.00]
[00:13.00]Second verse
```

## Compact Format

The compact format merges identical lyrics that appear at different times into a single line with multiple timestamps.
This is useful for repeated sections like choruses.

**Example:**

```lrc
Standard format:
[00:10.00]Chorus line here
[00:30.00]Chorus line here
[00:50.00]Chorus line here

Compact format:
[00:10.00][00:30.00][00:50.00]Chorus line here
```

> [!WARNING]
>
> - Not all LRC players support the compact format. Use the `expand` command to convert back to standard format if needed.
> - **Compact format doesn't support word timing**. If you use `--compact` with `--enhanced`, word timing will be
>   automatically disabled and a compact LRC without word timing will be generated.

## Architecture

The application is structured using OOP principles:

- **`models.py`**: Data classes for `Syllable`, `LyricLine`, and `Metadata`
- **`parser.py`**: `ASSParser` class for parsing ASS files
- **`lrc_parser.py`**: `LRCParser` class for parsing LRC files
- **`converter.py`**: `LRCConverter` class for generating LRC output
- **`ass_converter.py`**: `ASSConverter` class for generating ASS output
- **`expander.py`**: `LRCExpander` class for expanding compact format
- **`cli.py`**: Typer-based command-line interface

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py -v

# Run with coverage
pytest tests/ --cov=ass2lrc --cov-report=term-missing
```

### Code Quality

```bash
# Lint with ruff
task lint

# Format code
task format

# Type check
task typecheck

# Run all checks
task qa
```

### Using Task

Available commands:

```bash
task                 # Show all available tasks
task install         # Install package
task install-dev     # Install with dev dependencies
task test            # Run tests
task test-cov        # Run tests with coverage
task lint            # Run linter
task format          # Format code
task typecheck       # Type checking
task qa              # Run all quality checks
task clean           # Remove generated files
task build           # Build distribution packages
task publish-test    # Publish to TestPyPI
task publish         # Publish to PyPI
```

Install Task from: <https://taskfile.dev/installation/>

## License

See LICENSE file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Start

```bash
# Clone repository
git clone https://github.com/nattadasu/ass-to-lrc.git
cd ass-to-lrc

# Setup development environment (uses uv)
task dev

# Make changes and test
task qa
```

### Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/).

**Format**: `<type>(<scope>): <subject>`

**Example**: `feat(converter): Add compact LRC format support`

Pre-commit hooks will automatically validate your commits. See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.
