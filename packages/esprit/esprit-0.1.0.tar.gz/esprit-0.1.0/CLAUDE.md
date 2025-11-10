# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Esprit is a minimal terminal-based spreadsheet editor built with Textual (Python TUI framework). It supports structured tables with typed columns (string, URL), cell editing, selection ranges with sum calculation, and JSON persistence.

## Build, Test, and Development Commands

- `uv venv && source .venv/bin/activate` — create and activate a Python 3.12 virtual environment (preferred for all work)
- `python -m pip install -e .` — install esprit in editable mode along with Textual/Rich runtime dependencies
- `esprit` — launches the terminal UI - Claude show not do this since it is a
  TUI and messes up the input
- `esprit <file.json>` — open a specific JSON spreadsheet file on startup -
  Claude should not do this since it is a TUI a messes up the input
- `pytest` — run the test suite (add pytest to dev environment if not present)
- `ruff check` / `ruff format` — lint and format code
- `mypy` — run type checking

## Architecture

### Module Organization

The `esprit/` package contains four core modules with distinct responsibilities:

- **`model.py`** — Pure data layer (`SpreadsheetModel`). Handles all cell storage (keyed by `"row,col"`), column metadata (names and types), and JSON serialization/deserialization. Contains logic for URL parsing (`Title | https://...`) and type-specific cell value normalization.

- **`app.py`** — Main Textual application (`SpreadsheetApp`). Orchestrates the DataTable widget, cursor navigation, cell selection (shift+arrow keys), status bar updates, and event handlers. Manages editing mode toggle and delegates data operations to `SpreadsheetModel`.

- **`dialogs.py`** — Reusable modal dialog widgets (e.g., `SaveBeforeQuitDialog`). Overlays with callbacks for user decisions (save/quit/cancel).

- **`main.py`** — CLI entry point. Parses command-line arguments (optional file path) and launches `SpreadsheetApp`.

### Data Model Details

- **Metadata structure**: `metadata.columns` is a list of `{"name": "Column A", "type": "string"}` objects. The length of this list defines the number of columns.
- **Cell storage**: `cells` dict uses string keys `"row,col"` (0-indexed). Empty cells are absent from the dict.
- **URL cells**: Stored as `{"title": "Spec", "url": "https://..."}` dicts. In edit mode, displayed as `Title | https://...`. Press `ctrl+enter` to open the link.
- **Column types**: Currently `"string"` or `"url"`. Type checking happens via `get_column_type(col)`.

## Textual Framework Specifics

- Esprit uses [Textual](https://textual.textualize.io/) for TUI rendering.
- Refer to [Textual reference docs](https://textual.textualize.io/reference/) for widget APIs.
- **CSS differences**: Textual CSS is NOT browser CSS. Check [CSS types](https://textual.textualize.io/css_types/) before using properties.
- **Async event loop**: Avoid long-running blocking calls in action handlers. Move I/O to worker threads if needed.
- **Key bindings**: Defined in `SpreadsheetApp.BINDINGS`. Include `enter`, `ctrl+s`, `ctrl+q`, `ctrl+enter`, `escape`.

## Version Control

- **Do not run git commands**. This repo is managed with [Jujutsu (jj-vcs)](https://github.com/martinvonz/jj) and is typically in a detached HEAD state.
- The git status shown at conversation start is a snapshot and won't update.

## Testing

- Test files live in `tests/`. Mirror the runtime structure (`tests/test_model.py`, etc.).
- `tests/spreadsheet.json` contains fixture data for manual verification.
