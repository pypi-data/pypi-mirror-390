"""Model list widget."""

from textual.widgets import DataTable
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from typing import List
from cerebro.models import OllamaModel


class ModelList(VerticalScroll):
    """Widget for displaying a list of models."""
    
    DEFAULT_CSS = """
    ModelList {
        border: solid $primary;
        height: 1fr;
    }
    
    ModelList DataTable {
        height: 1fr;
    }
    
    ModelList DataTable > .datatable--cursor {
        background: $primary 20%;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.models: List[OllamaModel] = []
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        table = DataTable(cursor_type="row")
        table.add_columns("Name", "Size", "Modified")
        yield table
    
    def update_models(self, models: List[OllamaModel]) -> None:
        """Update the model list."""
        self.models = models
        table = self.query_one(DataTable)
        table.clear()
        
        for model in models:
            size_mb = model.size / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB" if size_mb < 1024 else f"{size_mb/1024:.1f} GB"
            modified_str = model.modified_at.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                model.name,
                size_str,
                modified_str,
                key=model.name
            )
    
    def get_selected_model(self) -> str | None:
        """Get the currently selected model name."""
        table = self.query_one(DataTable)
        if table.cursor_row >= 0 and table.cursor_row < len(self.models):
            return self.models[table.cursor_row].name
        return None