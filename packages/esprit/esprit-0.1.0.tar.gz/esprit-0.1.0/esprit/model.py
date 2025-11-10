"""Data model for the Esprit structured table editor."""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple


class SpreadsheetModel:
    """Holds all spreadsheet metadata, cells, and serialization helpers."""

    def __init__(self):
        self.rows = 20
        self.cols = 10
        self.metadata = self._default_metadata(self.cols)
        self.cells: Dict[str, Any] = {}

    def _default_metadata(self, columns: int) -> Dict[str, Any]:
        """Generate default column names/types when none are supplied."""
        column_defs = []
        for index in range(columns):
            label = self._column_label(index)
            column_defs.append({"name": label, "type": "string"})
        return {"title": "Untitled Spreadsheet", "columns": column_defs}

    def _column_label(self, index: int) -> str:
        base = chr(ord("A") + index) if index < 26 else f"{index + 1}"
        return f"Column {base}"

    def get_column_headers(self) -> list[str]:
        columns = self.metadata.get("columns", [])
        if not columns:
            self.metadata = self._default_metadata(self.cols)
            columns = self.metadata["columns"]
        return [
            col.get("name", self._column_label(idx)) for idx, col in enumerate(columns)
        ]

    def get_column_type(self, index: int) -> str:
        columns = self.metadata.get("columns", [])
        if 0 <= index < len(columns):
            return columns[index].get("type", "string")
        return "string"

    def get_title(self) -> str:
        """Get the spreadsheet title from metadata."""
        return self.metadata.get("title", "Untitled Spreadsheet")

    def set_title(self, title: str):
        """Set the spreadsheet title in metadata."""
        self.metadata["title"] = title if title.strip() else "Untitled Spreadsheet"

    def get_cell_raw(self, row: int, col: int) -> Any:
        key = f"{row},{col}"
        return self.cells.get(key)

    def get_cell(self, row: int, col: int) -> str:
        value = self.get_cell_raw(row, col)
        column_type = self.get_column_type(col)
        if column_type == "url":
            title, href = self._normalize_url_value(value)
            return title or href
        elif column_type == "number":
            return self.format_number(value)
        elif column_type == "boolean":
            return self.format_boolean(value)
        if value is None:
            return ""
        return str(value)

    def get_cell_status_text(self, row: int, col: int) -> str:
        value = self.get_cell_raw(row, col)
        column_type = self.get_column_type(col)
        if column_type == "url":
            title, href = self._normalize_url_value(value)
            if title and href:
                return f"{title} ({href})"
            return title or href
        if value is None:
            return ""
        return str(value)

    def get_cell_url(self, row: int, col: int) -> str:
        value = self.get_cell_raw(row, col)
        _, href = self._normalize_url_value(value)
        return href

    def get_url_edit_value(self, row: int, col: int) -> str:
        value = self.get_cell_raw(row, col)
        title, href = self._normalize_url_value(value)
        if title and href:
            return f"{title} | {href}"
        return title or href

    def parse_url_input(self, value: str) -> Tuple[str, str]:
        if not value:
            return "", ""
        if "|" in value:
            title, href = value.split("|", 1)
            return title.strip(), href.strip()
        value = value.strip()
        if self._looks_like_url(value):
            return "", value
        return value, ""

    def _normalize_url_value(self, value: Any) -> Tuple[str, str]:
        title, href = "", ""
        if isinstance(value, dict):
            title = str(value.get("title", "")).strip()
            href = str(value.get("url", "")).strip()
        elif isinstance(value, str):
            title, href = self.parse_url_input(value)
            if href == "" and self._looks_like_url(title):
                href = title
                title = ""
        if not href and self._looks_like_url(title):
            href = title
            title = ""
        return title, href

    def _looks_like_url(self, text: str) -> bool:
        return bool(text) and "://" in text

    def parse_number_input(self, value: str) -> Tuple[bool, float | None]:
        """Parse number input, return (is_valid, parsed_value)."""
        if not value or not value.strip():
            return True, None
        try:
            # Remove commas if present
            cleaned = value.strip().replace(",", "")
            parsed = float(cleaned)
            return True, parsed
        except ValueError:
            return False, None

    def format_number(self, value: Any) -> str:
        """Format number with comma separators."""
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            # Format with comma separators
            if isinstance(value, int) or value.is_integer():
                return f"{int(value):,}"
            else:
                # Format float with 2 decimal places
                return f"{value:,.2f}"
        return str(value)

    def parse_boolean_input(self, value: str) -> Tuple[bool, bool | None]:
        """Parse boolean input, return (is_valid, parsed_value)."""
        if not value or not value.strip():
            return True, None
        normalized = value.strip().lower()
        if normalized in ("true", "t", "yes", "y", "1"):
            return True, True
        elif normalized in ("false", "f", "no", "n", "0"):
            return True, False
        return False, None

    def format_boolean(self, value: Any) -> str:
        """Format boolean as checkmark/cross symbols."""
        if value is None:
            return ""
        if isinstance(value, bool):
            return "✓" if value else "✗"
        # Try to interpret other types
        if value in (1, "1", "true", "True", "yes", "Yes"):
            return "✓"
        return "✗"

    def set_cell(self, row: int, col: int, value: Any):
        key = f"{row},{col}"
        if value:
            self.cells[key] = value
        elif key in self.cells:
            del self.cells[key]

    def delete_row(self, row: int):
        """Delete a row and shift all rows below it up."""
        if row < 0 or row >= self.rows:
            return

        # Delete all cells in the row
        for col in range(self.cols):
            key = f"{row},{col}"
            if key in self.cells:
                del self.cells[key]

        # Shift all rows below up by one
        for r in range(row + 1, self.rows):
            for col in range(self.cols):
                old_key = f"{r},{col}"
                new_key = f"{r - 1},{col}"
                if old_key in self.cells:
                    self.cells[new_key] = self.cells[old_key]
                    del self.cells[old_key]
                elif new_key in self.cells:
                    # Clear the new position if old position was empty
                    del self.cells[new_key]

        # Decrement row count
        self.rows -= 1

    def insert_row(self, row: int):
        """Insert a new empty row at the specified position, shifting rows at and below down."""
        if row < 0 or row > self.rows:
            return

        # Shift all rows at and below down by one (process in reverse to avoid overwriting)
        for r in range(self.rows - 1, row - 1, -1):
            for col in range(self.cols):
                old_key = f"{r},{col}"
                new_key = f"{r + 1},{col}"
                if old_key in self.cells:
                    self.cells[new_key] = self.cells[old_key]
                    del self.cells[old_key]

        # The new row at 'row' is now empty (no cells need to be created)
        # Increment row count
        self.rows += 1

    def swap_rows(self, row1: int, row2: int):
        """Swap all cells between two rows."""
        if row1 < 0 or row1 >= self.rows or row2 < 0 or row2 >= self.rows:
            return
        if row1 == row2:
            return

        # Swap all cells in the two rows
        for col in range(self.cols):
            key1 = f"{row1},{col}"
            key2 = f"{row2},{col}"

            val1 = self.cells.get(key1)
            val2 = self.cells.get(key2)

            # Swap or delete as needed
            if val1 is not None and val2 is not None:
                # Both exist, swap them
                self.cells[key1] = val2
                self.cells[key2] = val1
            elif val1 is not None and val2 is None:
                # Only val1 exists, move it to row2
                self.cells[key2] = val1
                del self.cells[key1]
            elif val1 is None and val2 is not None:
                # Only val2 exists, move it to row1
                self.cells[key1] = val2
                del self.cells[key2]
            # If both are None, nothing to do

    def to_json(self) -> str:
        data = {
            "metadata": self.metadata,
            "rows": self.rows,
            "cols": self.cols,
            "cells": self.cells,
        }
        return json.dumps(data, indent=2)

    def from_json(self, json_str: str):
        data = json.loads(json_str)
        self.rows = data.get("rows", self.rows)
        self.cols = data.get("cols", self.cols)
        metadata = data.get("metadata")
        if metadata and metadata.get("columns"):
            self.metadata = metadata
            self.cols = len(self.metadata["columns"])
        else:
            self.metadata = self._default_metadata(self.cols)
        self.cells = data.get("cells", {})
