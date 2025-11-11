"""Site models screen for browsing Ollama library."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Label, Static, DataTable
from textual.binding import Binding
from cerebro.models import SiteModel
from typing import List


class SiteModelsScreen(Vertical):
    """Screen for browsing Ollama site models."""
    
    DEFAULT_CSS = """
    SiteModelsScreen {
        height: 1fr;
    }
    
    #filter-container {
        height: auto;
        padding: 1;
        background: $surface;
    }
    
    #filter-input {
        width: 1fr;
    }
    
    #models-table {
        height: 1fr;
    }
    
    #status-bar {
        height: 3;
        padding: 1;
        background: $panel;
        border-top: solid $primary;
    }
    
    .action-button {
        margin-left: 1;
    }
    
    DataTable {
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+r", "refresh_models", "Refresh"),
        Binding("ctrl+p", "pull_model", "Pull"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site_models: List[SiteModel] = []
        self.filtered_models: List[SiteModel] = []
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        with Horizontal(id="filter-container"):
            yield Input(
                placeholder="Filter site models...",
                id="filter-input"
            )
            yield Button("Refresh", id="refresh-button", variant="primary", classes="action-button")
            yield Button("Pull", id="pull-button", variant="success", classes="action-button")
        
        table = DataTable(cursor_type="row", id="models-table")
        table.add_columns("Name", "Description", "Tags")
        yield table
        
        with Vertical(id="status-bar"):
            yield Label("Status: Ready", id="status-label")
            yield Label("Models: 0", id="count-label")
    
    async def on_mount(self) -> None:
        """Handle mount event."""
        self.load_sample_models()
    
    def load_sample_models(self) -> None:
        """Load sample models (placeholder for actual API call)."""
        # In a real implementation, this would fetch from Ollama's API
        self.site_models = [
            SiteModel(
                name="llama3.2",
                description="Meta's Llama 3.2 model",
                tags=["3B", "1B"]
            ),
            SiteModel(
                name="llama3.1",
                description="Meta's Llama 3.1 model",
                tags=["8B", "70B", "405B"]
            ),
            SiteModel(
                name="llama3",
                description="Meta's Llama 3 model",
                tags=["8B", "70B"]
            ),
            SiteModel(
                name="mistral",
                description="Mistral AI's flagship model",
                tags=["7B"]
            ),
            SiteModel(
                name="mixtral",
                description="Mistral AI's mixture of experts model",
                tags=["8x7B", "8x22B"]
            ),
            SiteModel(
                name="phi3",
                description="Microsoft's Phi-3 model",
                tags=["mini", "small", "medium"]
            ),
            SiteModel(
                name="gemma2",
                description="Google's Gemma 2 model",
                tags=["2B", "9B", "27B"]
            ),
            SiteModel(
                name="qwen2.5",
                description="Alibaba's Qwen 2.5 model",
                tags=["0.5B", "1.5B", "3B", "7B", "14B", "32B", "72B"]
            ),
            SiteModel(
                name="deepseek-r1",
                description="DeepSeek's reasoning model",
                tags=["1.5B", "7B", "8B", "14B", "32B", "70B", "671B"]
            ),
            SiteModel(
                name="llava",
                description="Vision language model",
                tags=["7B", "13B", "34B"]
            ),
        ]
        
        self.filtered_models = self.site_models.copy()
        self.update_table()
    
    def update_table(self) -> None:
        """Update the models table."""
        table = self.query_one("#models-table", DataTable)
        table.clear()
        
        for model in self.filtered_models:
            tags_str = ", ".join(model.tags)
            table.add_row(
                model.name,
                model.description,
                tags_str,
                key=model.name
            )
        
        count_label = self.query_one("#count-label", Label)
        count_label.update(f"Models: {len(self.filtered_models)}")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        if event.input.id == "filter-input":
            filter_text = event.value.lower()
            
            if not filter_text:
                self.filtered_models = self.site_models.copy()
            else:
                self.filtered_models = [
                    model for model in self.site_models
                    if filter_text in model.name.lower() or 
                       filter_text in model.description.lower() or
                       any(filter_text in tag.lower() for tag in model.tags)
                ]
            
            self.update_table()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-button":
            await self.action_refresh_models()
        elif event.button.id == "pull-button":
            await self.action_pull_model()
    
    async def action_refresh_models(self) -> None:
        """Action to refresh models."""
        status_label = self.query_one("#status-label", Label)
        status_label.update("Status: Refreshing...")
        
        # In real implementation, fetch from API
        self.load_sample_models()
        
        status_label.update("Status: Ready")
    
    async def action_pull_model(self) -> None:
        """Action to pull selected model."""
        table = self.query_one("#models-table", DataTable)
        
        if table.cursor_row >= 0 and table.cursor_row < len(self.filtered_models):
            model = self.filtered_models[table.cursor_row]
            status_label = self.query_one("#status-label", Label)
            status_label.update(f"Status: Pull {model.name} - not implemented in minimal version")
            
            # In real implementation:
            # async for progress in self.ollama_service.pull_model(model.name):
            #     status_label.update(f"Pulling: {progress}")
    
    def refresh_models(self) -> None:
        """Refresh models list."""
        self.load_sample_models()