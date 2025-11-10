"""Textual application for the Esprit structured table editor."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Input, Label

from .dialogs import InitDialog
from .model import SpreadsheetModel


class SpreadsheetApp(App):
    CSS = """
    DataTable {
        height: 1fr;
    }
    
    DataTable > .datatable--header {
        height: 2;
        padding: 1;
    }
    
    DataTable > .datatable--body {
        height: 1fr;
    }
    
    DataTable .datatable--cursor {
        background: $accent 50%;
        color: $text;
        padding: 1;
    }
    
    DataTable .datatable--hover {
        background: $surface;
    }
    
    DataTable .datatable--cell {
        padding: 1;
    }
    
    .selected-cell {
        background: $primary 30%;
        color: $text;
    }
    
    #status {
        height: 2;
        dock: bottom;
        background: $accent;
        color: $text;
        text-style: bold;
        display: block;
    }
    
    #cell_input {
        height: 3;
        dock: bottom;
        margin-bottom: 2;
        display: none;
    }
    """

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+i", "insert_row", "Insert Row"),
        ("ctrl+k", "delete_row", "Delete Row"),
        ("alt+up", "move_row_up", "Move Row Up"),
        ("alt+down", "move_row_down", "Move Row Down"),
        ("ctrl+enter", "open_link", "Open Link"),
        ("enter", "edit_cell", "Edit"),
        ("escape", "cancel_edit", "Cancel"),
    ]

    def __init__(self, start_file: Optional[Path] = None):
        super().__init__()
        self.model = SpreadsheetModel()
        self.current_file: Optional[Path] = None
        self.input_mode = None  # Can be: None, "cell_edit", "command"
        self.command_callback = None  # Callback for command mode
        self.selection_start = None  # (row, col) of selection start
        self.selection_end = None  # (row, col) of selection end
        self.selected_cells = set()  # Set of (row, col) tuples
        self.start_file = start_file
        self.dirty = False
        self.default_input_placeholder = "Enter cell value..."
        self.init_dialog: Optional[InitDialog] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="spreadsheet")
        yield Label("", id="status")
        yield Input(placeholder=self.default_input_placeholder, id="cell_input")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#spreadsheet", DataTable)
        table.cursor_type = "cell"

        # Check if we need to show init dialog for a new file
        if self.start_file and not self.start_file.exists():
            # Show init dialog without populating table
            self.show_init_dialog()
            return

        # Otherwise, populate the table normally
        # Set the title from model
        self.title = self.model.get_title()

        # Add column headers from metadata
        columns = [""] + self.model.get_column_headers()
        table.add_columns(*columns)

        # Add rows with row numbers and cell values
        for row in range(self.model.rows):
            row_data = [str(row + 1)]
            for col in range(self.model.cols):
                value = self.model.get_cell(row, col)
                row_data.append(value if value else " " * 4)  # Make cells wider
            table.add_row(*row_data, key=f"row_{row}")

        # Load existing file if specified
        if self.start_file and self.start_file.exists():
            self.load_file(self.start_file)

    def refresh_table(self):
        table = self.query_one("#spreadsheet", DataTable)
        table.clear(columns=True)  # Clear both rows and columns
        table.cursor_type = "cell"

        # Add column headers from metadata
        columns = [""] + self.model.get_column_headers()
        table.add_columns(*columns)

        # Add rows with row numbers and cell values
        for row in range(self.model.rows):
            row_data = [str(row + 1)]
            for col in range(self.model.cols):
                value = self.model.get_cell(row, col)
                cell_value = value if value else " " * 4

                # Apply styling if cell is selected
                if (row, col) in self.selected_cells:
                    cell_text = Text(cell_value, style="black on yellow")
                    row_data.append(cell_text)
                else:
                    row_data.append(cell_value)
            table.add_row(*row_data, key=f"row_{row}")

    def get_cell_address(self, row: int, col: int) -> str:
        headers = self.model.get_column_headers()
        column_label = headers[col] if col < len(headers) else f"Col {col + 1}"
        return f"{column_label} {row + 1}"

    def update_status(self, row: int, col: int):
        status = self.query_one("#status", Label)

        if len(self.selected_cells) > 1:
            # Show selection info and sum
            total = self.calculate_selection_sum()
            count = len(self.selected_cells)

            # Show selection range
            start_addr = self.get_cell_address(*self.selection_start)
            end_addr = self.get_cell_address(*self.selection_end)
            status.update(
                f"Selected {start_addr}:{end_addr} ({count} cells) | Sum: {total}"
            )
        elif self.model.get_column_type(col) == "url":
            # Show URL for URL columns
            value = self.model.get_cell_status_text(row, col)
            if value:
                status.update(value)
            else:
                status.update("")
        else:
            # Clear status for regular cells
            status.update("")

    def force_update_status(self):
        status = self.query_one("#status", Label)
        if len(self.selected_cells) > 1:
            # Show selection info and sum
            total = self.calculate_selection_sum()
            count = len(self.selected_cells)

            # Show selection range
            start_addr = self.get_cell_address(*self.selection_start)
            end_addr = self.get_cell_address(*self.selection_end)
            status.update(
                f"Selected {start_addr}:{end_addr} ({count} cells) | Sum: {total}"
            )
        else:
            table = self.query_one("#spreadsheet", DataTable)
            if table.cursor_coordinate and table.cursor_coordinate.column > 0:
                row = table.cursor_coordinate.row
                col = table.cursor_coordinate.column - 1
                if self.model.get_column_type(col) == "url":
                    # Show URL for URL columns
                    value = self.model.get_cell_status_text(row, col)
                    if value:
                        status.update(value)
                    else:
                        status.update("")
                else:
                    # Clear status for regular cells
                    status.update("")

    def update_status_from_cursor(self):
        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate and table.cursor_coordinate.column > 0:
            row = table.cursor_coordinate.row
            col = table.cursor_coordinate.column - 1
            self.update_status(row, col)

    def clear_selection(self):
        if len(self.selected_cells) > 0:
            self.selection_start = None
            self.selection_end = None
            self.selected_cells.clear()
            # Refresh table to remove selection styling
            table = self.query_one("#spreadsheet", DataTable)
            cursor_pos = table.cursor_coordinate
            self.refresh_table()
            # Restore cursor position
            if cursor_pos:
                table.move_cursor(row=cursor_pos.row, column=cursor_pos.column)

    def handle_shift_selection(self, key):
        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is None or table.cursor_coordinate.column == 0:
            return

        current_row = table.cursor_coordinate.row
        current_col = table.cursor_coordinate.column - 1  # Adjust for row number column

        # Start selection if not already started
        if self.selection_start is None:
            self.selection_start = (current_row, current_col)

        # Move cursor based on key
        new_row, new_col = current_row, current_col
        if key == "shift+up" and current_row > 0:
            new_row = current_row - 1
        elif key == "shift+down" and current_row < self.model.rows - 1:
            new_row = current_row + 1
        elif key == "shift+left" and current_col > 0:
            new_col = current_col - 1
        elif key == "shift+right" and current_col < self.model.cols - 1:
            new_col = current_col + 1

        # Update selection end
        self.selection_end = (new_row, new_col)
        self.update_selected_cells()

        # Refresh table to show selection styling
        self.refresh_table()

        # Move the cursor to the new position
        table.move_cursor(row=new_row, column=new_col + 1)

        # Force status update for selection
        self.force_update_status()

    def update_selected_cells(self):
        if self.selection_start is None or self.selection_end is None:
            return

        start_row, start_col = self.selection_start
        end_row, end_col = self.selection_end

        # Ensure proper ordering
        min_row, max_row = min(start_row, end_row), max(start_row, end_row)
        min_col, max_col = min(start_col, end_col), max(start_col, end_col)

        # Update selected cells set
        self.selected_cells.clear()
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                self.selected_cells.add((row, col))

    def calculate_selection_sum(self):
        total = 0
        for row, col in self.selected_cells:
            value = self.model.get_cell(row, col)
            try:
                # Try to convert to number
                if value:
                    total += float(value)
            except ValueError:
                # Skip non-numeric values
                pass
        return total

    def on_data_table_cell_selected(self, event: DataTable.CellSelected):
        if event.coordinate.column != 0:  # Skip row number column
            col = event.coordinate.column - 1  # Adjust for row number column
            row = event.coordinate.row
            self.update_status(row, col)

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted):
        if event.coordinate.column != 0:  # Skip row number column
            col = event.coordinate.column - 1  # Adjust for row number column
            row = event.coordinate.row
            self.update_status(row, col)

    def on_key(self, event):
        if self.init_dialog is not None:
            return
        if event.key == "enter" and self.input_mode is None:
            self.action_edit_cell()
            event.prevent_default()
        elif self.input_mode is None:
            # Check for shift+arrow key combinations
            if str(event.key) in [
                "shift+up",
                "shift+down",
                "shift+left",
                "shift+right",
            ]:
                self.handle_shift_selection(str(event.key))
                event.prevent_default()
            elif str(event.key) in ["up", "down", "left", "right"]:
                # Clear selection on normal navigation
                self.clear_selection()

    def action_edit_cell(self):
        if self.init_dialog is not None:
            return
        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is not None:
            if table.cursor_coordinate.column != 0:  # Skip row number column
                col = table.cursor_coordinate.column - 1  # Adjust for row number column
                row = table.cursor_coordinate.row

                cell_input = self.query_one("#cell_input", Input)
                column_type = self.model.get_column_type(col)
                if column_type == "url":
                    cell_input.placeholder = "Title | https://example.com"
                    cell_input.value = self.model.get_url_edit_value(row, col)
                elif column_type == "number":
                    cell_input.placeholder = "Enter a number..."
                    # Show raw value for editing (without formatting)
                    raw_value = self.model.get_cell_raw(row, col)
                    cell_input.value = str(raw_value) if raw_value is not None else ""
                elif column_type == "boolean":
                    cell_input.placeholder = "true/false, yes/no, 1/0"
                    raw_value = self.model.get_cell_raw(row, col)
                    if raw_value is True:
                        cell_input.value = "true"
                    elif raw_value is False:
                        cell_input.value = "false"
                    else:
                        cell_input.value = ""
                else:
                    cell_input.placeholder = self.default_input_placeholder
                    cell_input.value = self.model.get_cell(row, col)
                cell_input.display = True
                cell_input.focus()
                self.input_mode = "cell_edit"

    def action_cancel_edit(self):
        if self.input_mode is not None:
            cell_input = self.query_one("#cell_input", Input)
            cell_input.display = False
            cell_input.value = ""
            cell_input.placeholder = self.default_input_placeholder
            self.input_mode = None
            self.command_callback = None
            table = self.query_one("#spreadsheet", DataTable)
            table.focus()

    def on_input_submitted(self, event: Input.Submitted):
        if self.input_mode == "cell_edit":
            self._handle_cell_edit(event)
        elif self.input_mode == "command":
            self._handle_command(event)

    def _handle_cell_edit(self, event: Input.Submitted):
        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is not None:
            if table.cursor_coordinate.column != 0:  # Skip row number column
                col = table.cursor_coordinate.column - 1  # Adjust for row number column
                row = table.cursor_coordinate.row

                value = event.input.value
                column_type = self.model.get_column_type(col)
                if column_type == "url":
                    title, href = self.model.parse_url_input(value)
                    if not title and not href:
                        self.model.set_cell(row, col, "")
                    else:
                        data = {"title": title, "url": href}
                        self.model.set_cell(row, col, data)
                elif column_type == "number":
                    is_valid, parsed = self.model.parse_number_input(value)
                    if not is_valid:
                        self.notify("Invalid number format", severity="error")
                        return
                    self.model.set_cell(row, col, parsed)
                elif column_type == "boolean":
                    is_valid, parsed = self.model.parse_boolean_input(value)
                    if not is_valid:
                        self.notify(
                            "Invalid boolean value (use true/false, yes/no, 1/0)",
                            severity="error",
                        )
                        return
                    self.model.set_cell(row, col, parsed)
                else:
                    self.model.set_cell(row, col, value)
                self.dirty = True
                # Refresh the entire table to show the update
                cursor_pos = table.cursor_coordinate
                self.refresh_table()
                # Restore cursor position
                if cursor_pos:
                    table.move_cursor(row=cursor_pos.row, column=cursor_pos.column)

        event.input.display = False
        event.input.value = ""
        event.input.placeholder = self.default_input_placeholder
        self.input_mode = None
        table.focus()

    def _handle_command(self, event: Input.Submitted):
        """Handle command mode input."""
        value = event.input.value.strip().lower()

        # Hide input and reset state
        event.input.display = False
        event.input.value = ""
        event.input.placeholder = self.default_input_placeholder

        # Call the callback with the response
        if self.command_callback:
            self.command_callback(value)
            self.command_callback = None

        self.input_mode = None
        table = self.query_one("#spreadsheet", DataTable)
        table.focus()

    def _show_command_prompt(self, prompt: str, callback):
        """Show the command input with a prompt and callback."""
        cell_input = self.query_one("#cell_input", Input)
        cell_input.placeholder = prompt
        cell_input.value = ""
        cell_input.display = True
        cell_input.focus()
        self.input_mode = "command"
        self.command_callback = callback

    def action_save(self):
        if self.current_file is None:
            self.current_file = Path("spreadsheet.json")

        try:
            with open(self.current_file, "w") as f:
                f.write(self.model.to_json())
            self.notify(f"Saved to {self.current_file}")
            self.dirty = False
        except Exception as e:
            self.notify(f"Error saving: {e}", severity="error")

    def load_file(self, file_path: Path):
        try:
            with open(file_path, "r") as f:
                self.model.from_json(f.read())
            self.current_file = file_path
            self.title = self.model.get_title()
            self.refresh_table()
            self.dirty = False
        except FileNotFoundError:
            self.notify(f"{file_path} not found", severity="warning")
        except Exception as e:
            self.notify(f"Error opening {file_path}: {e}", severity="error")

    def action_quit(self):
        if self.dirty:
            self._show_command_prompt(
                "Save changes before quitting? (Y/n/cancel)", self._handle_quit_response
            )
        else:
            self.exit()

    def _handle_quit_response(self, response: str):
        """Handle the user's response to the quit prompt."""
        # Default to yes if empty (just pressed enter)
        if response == "" or response in ["y", "yes"]:
            self.action_save()
            if not self.dirty:
                self.exit()
        elif response in ["n", "no"]:
            self.exit()
        # Any other response (including "cancel") just returns to normal mode

    def action_open_link(self):
        if self.input_mode is not None:
            return
        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is None or table.cursor_coordinate.column == 0:
            return
        col = table.cursor_coordinate.column - 1
        row = table.cursor_coordinate.row
        if self.model.get_column_type(col) != "url":
            self.notify("Select a URL column cell to open", severity="warning")
            return
        href = self.model.get_cell_url(row, col)
        if href:
            webbrowser.open(href)
            self.notify(f"Opening {href}")
        else:
            self.notify("No URL set for this cell", severity="warning")

    def action_insert_row(self):
        """Insert a new empty row above the current row."""
        if self.input_mode is not None or self.init_dialog is not None:
            return

        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is None:
            return

        row = table.cursor_coordinate.row
        cursor_col = table.cursor_coordinate.column

        # Insert the row
        self.model.insert_row(row)
        self.dirty = True

        # Refresh the table
        self.refresh_table()

        # Keep cursor at the newly inserted row
        table.move_cursor(row=row, column=cursor_col)

        self.notify(f"Inserted row at {row + 1}")

    def action_delete_row(self):
        """Delete the current row and shift rows below up."""
        if self.input_mode is not None or self.init_dialog is not None:
            return

        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is None:
            return

        row = table.cursor_coordinate.row

        # Don't allow deleting if only one row remains
        if self.model.rows <= 1:
            self.notify("Cannot delete the last row", severity="warning")
            return

        # Delete the row
        self.model.delete_row(row)
        self.dirty = True

        # Refresh the table
        cursor_col = table.cursor_coordinate.column
        self.refresh_table()

        # Move cursor to same column, but adjust row if needed
        new_row = min(row, self.model.rows - 1)
        table.move_cursor(row=new_row, column=cursor_col)

        self.notify(f"Deleted row {row + 1}")

    def action_move_row_up(self):
        """Move the current row up by swapping with the row above."""
        if self.input_mode is not None or self.init_dialog is not None:
            return

        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is None:
            return

        row = table.cursor_coordinate.row

        # Can't move the first row up
        if row == 0:
            return

        # Swap with the row above
        self.model.swap_rows(row, row - 1)
        self.dirty = True

        # Refresh the table
        cursor_col = table.cursor_coordinate.column
        self.refresh_table()

        # Move cursor up with the row
        table.move_cursor(row=row - 1, column=cursor_col)

    def action_move_row_down(self):
        """Move the current row down by swapping with the row below."""
        if self.input_mode is not None or self.init_dialog is not None:
            return

        table = self.query_one("#spreadsheet", DataTable)
        if table.cursor_coordinate is None:
            return

        row = table.cursor_coordinate.row

        # Can't move the last row down
        if row >= self.model.rows - 1:
            return

        # Swap with the row below
        self.model.swap_rows(row, row + 1)
        self.dirty = True

        # Refresh the table
        cursor_col = table.cursor_coordinate.column
        self.refresh_table()

        # Move cursor down with the row
        table.move_cursor(row=row + 1, column=cursor_col)

    def show_init_dialog(self):
        """Show the initialization dialog for creating a new spreadsheet."""
        if self.init_dialog is None:
            self.init_dialog = InitDialog(self._handle_init_complete)
            self.mount(self.init_dialog)

    def _handle_init_complete(self, data: dict | None):
        """Handle completion of the init dialog."""
        self.init_dialog = None
        if data:
            # Initialize model with the specified title and columns
            columns = data.get("columns", [])
            title = data.get("title", "Untitled Spreadsheet")
            self.model.metadata = {"title": title, "columns": columns}
            self.model.cols = len(columns)
            self.model.rows = 20  # Default number of rows
            self.model.cells = {}
            self.current_file = self.start_file
            self.title = title
            self.refresh_table()
            self.dirty = True  # Mark as dirty so it gets saved
            self.notify(f"Initialized new spreadsheet with {len(columns)} columns")
        else:
            # User cancelled, exit the application
            self.exit()
