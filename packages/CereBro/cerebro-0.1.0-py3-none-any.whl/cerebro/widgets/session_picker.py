"""Session picker dialog."""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import DataTable, Button, Label, Input
from textual.binding import Binding
from cerebro.models import ChatSession
from typing import List, Optional


class SessionPicker(ModalScreen):
    """Modal dialog for picking a chat session."""
    
    DEFAULT_CSS = """
    SessionPicker {
        align: center middle;
    }
    
    #dialog {
        width: 80;
        height: 30;
        border: thick $primary;
        background: $panel;
        padding: 1;
    }
    
    #dialog-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }
    
    #sessions-table {
        height: 1fr;
        margin-bottom: 1;
    }
    
    #button-container {
        height: auto;
        align: center middle;
    }
    
    #filter-box {
        margin-bottom: 1;
    }
    
    .dialog-button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
    ]
    
    def __init__(self, sessions: List[ChatSession], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions = sorted(sessions, key=lambda s: s.updated_at, reverse=True)
        self.filtered_sessions = self.sessions.copy()
        self.selected_session: Optional[ChatSession] = None
    
    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Vertical(id="dialog"):
            yield Label("📚 Load Chat Session", id="dialog-title")
            
            yield Input(
                placeholder="Filter sessions...",
                id="filter-box"
            )
            
            table = DataTable(cursor_type="row", id="sessions-table")
            table.add_columns("Name", "Model", "Messages", "Last Updated")
            yield table
            
            with Horizontal(id="button-container"):
                yield Button("Load", variant="primary", classes="dialog-button", id="load-btn")
                yield Button("Delete", variant="error", classes="dialog-button", id="delete-btn")
                yield Button("Cancel", classes="dialog-button", id="cancel-btn")
    
    def on_mount(self) -> None:
        """Handle mount event."""
        self.update_table()
    
    def update_table(self) -> None:
        """Update the sessions table."""
        table = self.query_one("#sessions-table", DataTable)
        table.clear()
        
        for session in self.filtered_sessions:
            msg_count = len(session.messages)
            updated = session.updated_at.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                session.name,
                session.model,
                str(msg_count),
                updated,
                key=session.id
            )
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        filter_text = event.value.lower()
        
        if not filter_text:
            self.filtered_sessions = self.sessions.copy()
        else:
            self.filtered_sessions = [
                s for s in self.sessions
                if filter_text in s.name.lower() or filter_text in s.model.lower()
            ]
        
        self.update_table()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "load-btn":
            self.action_select()
        elif event.button.id == "delete-btn":
            self.delete_selected()
        elif event.button.id == "cancel-btn":
            self.action_cancel()
    
    def action_select(self) -> None:
        """Select the highlighted session."""
        table = self.query_one("#sessions-table", DataTable)
        
        if table.cursor_row >= 0 and table.cursor_row < len(self.filtered_sessions):
            self.selected_session = self.filtered_sessions[table.cursor_row]
            self.dismiss(self.selected_session)
    
    def delete_selected(self) -> None:
        """Delete the selected session."""
        table = self.query_one("#sessions-table", DataTable)
        
        if table.cursor_row >= 0 and table.cursor_row < len(self.filtered_sessions):
            session_to_delete = self.filtered_sessions[table.cursor_row]
            
            # Remove from lists
            self.sessions.remove(session_to_delete)
            self.filtered_sessions.remove(session_to_delete)
            
            # Delete from disk (we'll need to pass chat_service)
            # For now, just update the table
            self.update_table()
    
    def action_cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)