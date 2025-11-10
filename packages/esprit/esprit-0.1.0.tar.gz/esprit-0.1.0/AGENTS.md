# Repository Guidelines

## Project Structure & Module Organization

- `esprit/` is the installable package. `app.py` hosts the Textual `SpreadsheetApp`, `model.py` contains the serialization/data logic, `screens.py` keeps modal dialogs (e.g., save prompts), and `main.py` is the thin CLI entry point. Add related features to the closest module or a new sibling to keep responsibilities narrow.
- `tests/` currently contains the `spreadsheet.json` fixture used for manual verification. Add automated tests here and mirror the runtime layout (`tests/test_model.py`, `tests/data/…`).

## Build, Test, and Development Commands
- `uv venv && source .venv/bin/activate` — create and activate a Python 3.12 virtual environment (preferred for all work).
- `python -m pip install -e .` — install esprit in editable mode along with Textual/Rich runtime dependencies.
- `esprit` — launch the terminal UI; accepts the same key bindings documented in `SpreadsheetApp.BINDINGS`.
- `pytest` — run the growing test suite (add `pytest` to your dev environment if not already present).

## Coding Style & Naming Conventions
- Use ruff check/format
- Use type hints
- Run mypy to confirm tpye checks

## TUI

- esprit uses Textual for its TUI framework
- Refer to Textual reference and documentation for proper use
- https://textual.textualize.io/reference/
- Textual CSS is not standard CSS in a browser, similar but confirm properties
  exist before making up and using. https://textual.textualize.io/css_types/


## Commit & Pull Request Guidelines

- Do not issue any git commands
- This project uses jujutsu vcs (jj)

## Configuration & Data Tips

- Persist spreadsheets using `SpreadsheetModel.to_json()`
- Sample data lives in `tests/spreadsheet.json`
- `metadata.columns` defines display names and field types (`string` or `url`) 
- `cells` keeps row/column keyed values—always keep `cols` in sync with the metadata length.
- URL cells persist as `{"title": "Spec", "url": "https://…"}`
- In-app editing of URL cells accepts `Title | https://…` and `ctrl+enter` launches the stored link.
- Respect Textual’s async event loop: avoid long-running blocking calls inside action handlers
- Move I/O to worker threads or preprocess data before attaching it to the UI.


## Instructions

- Do not run git commands. The repo is managed using jujutsu (jj-vcs) and is
  typically in a detached head state.
