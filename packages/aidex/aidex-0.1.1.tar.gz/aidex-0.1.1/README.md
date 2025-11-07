# Aidex

A terminal UI application built with [Textual](https://github.com/Textualize/textual).

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone and setup
git clone <your-repo>
cd aidex
uv sync

# Run the app
uv run aidex

# Check version
uv run aidex --version
```

## Project Structure

```
aidex/
├── __init__.py      # Package initialization
└── app.py           # Textual app + CLI entry point
```

## Adding Dependencies

```bash
uv add package-name
```
