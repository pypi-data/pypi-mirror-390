"""Reusable dialog widgets for the Esprit Textual app."""

from __future__ import annotations

from typing import Callable, Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static


class InitDialog(Static):
    """Dialog for initializing a new spreadsheet with column specifications."""

    DEFAULT_CSS = """
    InitDialog {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    InitDialog > Vertical {
        background: $panel;
        border: round $accent;
        padding: 2 4;
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #init_title {
        text-align: center;
        margin: 0 0 1 0;
        text-style: bold;
    }

    #title_input {
        width: 100%;
        margin: 1 0;
    }

    #column_list {
        height: 16;
        border: solid $primary;
        padding: 1;
        margin: 1 0;
    }

    .column_row {
        height: auto;
        margin: 0 0 1 0;
    }

    .column_row Input {
        width: 1fr;
        margin: 0 1 0 0;
    }

    .column_row Select {
        width: 20;
        margin: 0 1 0 0;
    }

    .column_row Button {
        width: 10;
    }

    #init_actions {
        content-align: center middle;
        margin: 1 0 0 0;
    }

    #init_actions Button {
        width: 16;
        margin: 0 1;
    }
    """

    def __init__(self, on_complete: Callable[[Optional[dict]], None]):
        super().__init__()
        self._on_complete = on_complete
        self._column_rows = []
        self._next_column_id = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Initialize New Spreadsheet", id="init_title")
            yield Input(
                placeholder="Spreadsheet Title",
                value="Untitled Spreadsheet",
                id="title_input",
            )
            with VerticalScroll(id="column_list"):
                # Start with 3 default columns
                for i in range(3):
                    yield from self._create_column_row_compose(i)
            with Horizontal(id="init_actions"):
                yield Button("Add Column", id="add_column", variant="default")
                yield Button("Create", id="create", variant="primary")
                yield Button("Cancel", id="cancel")

    def _create_column_row_compose(self, index: int) -> ComposeResult:
        """Create a row for initial composition using context manager pattern."""
        row_id = f"col_row_{self._next_column_id}"
        self._column_rows.append(self._next_column_id)
        col_id = self._next_column_id
        self._next_column_id += 1

        with Horizontal(classes="column_row", id=row_id):
            yield Input(
                placeholder=f"Column {index + 1} name",
                value=f"Column {chr(65 + index) if index < 26 else index + 1}",
                id=f"col_name_{col_id}",
            )
            yield Select(
                options=[
                    ("String", "string"),
                    ("Number", "number"),
                    ("Boolean", "boolean"),
                    ("URL", "url"),
                ],
                value="string",
                id=f"col_type_{col_id}",
            )
            yield Button("Remove", id=f"remove_{col_id}", variant="error")

    async def _create_column_row_dynamic(self, index: int) -> None:
        """Create and mount a row dynamically after initial composition."""
        row_id = f"col_row_{self._next_column_id}"
        self._column_rows.append(self._next_column_id)
        col_id = self._next_column_id
        self._next_column_id += 1

        # Get the parent container
        parent = self.query_one("#column_list")

        # Mount the row container first
        container = Horizontal(classes="column_row", id=row_id)
        await parent.mount(container)

        # Then mount children into the container
        await container.mount(
            Input(
                placeholder=f"Column {index + 1} name",
                value=f"Column {chr(65 + index) if index < 26 else index + 1}",
                id=f"col_name_{col_id}",
            ),
            Select(
                options=[
                    ("String", "string"),
                    ("Number", "number"),
                    ("Boolean", "boolean"),
                    ("URL", "url"),
                ],
                value="string",
                id=f"col_type_{col_id}",
            ),
            Button("Remove", id=f"remove_{col_id}", variant="error"),
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "add_column":
            # Add a new column row
            new_index = len(self._column_rows)
            await self._create_column_row_dynamic(new_index)
            event.stop()
        elif button_id == "create":
            # Gather title and column specifications
            title_input = self.query_one("#title_input", Input)
            title = title_input.value.strip() or "Untitled Spreadsheet"

            columns = self._gather_columns()
            if columns:
                data = {"title": title, "columns": columns}
                if self._on_complete:
                    self._on_complete(data)
                self.remove()
            else:
                # Show error if no valid columns
                self.app.notify("Please specify at least one column", severity="error")
            event.stop()
        elif button_id == "cancel":
            if self._on_complete:
                self._on_complete(None)
            self.remove()
            event.stop()
        elif button_id.startswith("remove_"):
            # Remove the column row
            col_id = button_id.replace("remove_", "")
            row_id = f"col_row_{col_id}"
            row = self.query_one(f"#{row_id}")
            if len(self._column_rows) > 1:
                row.remove()
                self._column_rows.remove(int(col_id))
            else:
                self.app.notify("Cannot remove the last column", severity="warning")
            event.stop()

    def _gather_columns(self) -> list[dict] | None:
        """Gather all column specifications from the form."""
        columns = []
        for col_id in self._column_rows:
            try:
                name_input = self.query_one(f"#col_name_{col_id}", Input)
                type_select = self.query_one(f"#col_type_{col_id}", Select)

                name = name_input.value.strip()
                if not name:
                    name = f"Column {len(columns) + 1}"

                col_type = type_select.value if type_select.value else "string"

                columns.append({"name": name, "type": col_type})
            except Exception:
                # Skip rows that couldn't be found (maybe removed)
                continue

        return columns if columns else None
