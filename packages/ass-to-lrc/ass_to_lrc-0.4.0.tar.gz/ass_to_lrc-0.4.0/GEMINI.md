# Project Overview

This project is a Python command-line application named `ass-to-lrc`.
It converts subtitle files from the Advanced SubStation Alpha (ASS) format to the LyRiCs (LRC) format.
The key feature is preserving word-level timing from karaoke tags to generate an "enhanced" LRC file.

The project is built using modern Python tools and practices.
It uses `typer` for the CLI, `hatch` for project management, and the `ass` library for parsing.
The codebase is well-structured, with separate modules for parsing, converting, and handling the CLI.

## Building and Running

The project uses `hatch` for build management and `pytest` for testing. The main commands are:

* **Installation:**

  ```bash
  pip install -e .
  ```

* **Running the application:**

  ```bash
  ass2lrc convert <input.ass>
  ```

* **Running tests:**

  ```bash
  pytest
  ```

## Development Conventions

The project follows standard Python development conventions.

* **Linting and Formatting:** The project uses `ruff` for linting and formatting.
  The configuration is in `pyproject.toml`.
* **Type Checking:** `mypy` is used for static type checking. The configuration is in `pyproject.toml`.
* **Testing:** `pytest` is used for running unit and integration tests.
  Tests are located in the `tests/` directory.
* **Commit Style:** The project follows the Conventional Commits specification.
* **Task Management:** The project uses `Taskfile.yml` to define common development tasks.
