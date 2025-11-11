"""Local models screen."""

from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Label, Static
from textual.binding import Binding
from textual.message import Message
from cerebro.widgets.model_list import ModelList
from cerebro.services.ollama_service import OllamaService


class LocalModelsScreen(Vertical):
    """Screen for managing local models."""
    
    DEFAULT_CSS = """
    LocalModelsScreen {
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
    
    #models-container {
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
    """
    
    BINDINGS = [
        Binding("ctrl+r", "refresh_models", "Refresh"),
        Binding("ctrl+d", "delete_model", "Delete"),
        Binding("ctrl+c", "copy_to_chat", "Use in Chat"),
    ]
    
    class ModelSelected(Message):
        """Message sent when a model is selected for chat."""
        
        def __init__(self, model_name: str) -> None:
            super().__init__()
            self.model_name = model_name
    
    def __init__(self, ollama_service: OllamaService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ollama_service = ollama_service
        self.all_models = []
        self.filtered_models = []
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        with Horizontal(id="filter-container"):
            yield Input(
                placeholder="Filter local models...",
                id="filter-input"
            )
            yield Button("Refresh", id="refresh-button", variant="primary", classes="action-button")
            yield Button("Delete", id="delete-button", variant="error", classes="action-button")
        
        with Vertical(id="models-container"):
            yield ModelList(id="model-list")
        
        with Vertical(id="status-bar"):
            yield Label("Status: Ready", id="status-label")
            yield Label("Models: 0", id="count-label")
    
    async def on_mount(self) -> None:
        """Handle mount event."""
        await self.refresh_models()
    
    async def refresh_models(self) -> None:
        """Refresh the list of local models."""
        status_label = self.query_one("#status-label", Label)
        status_label.update("Status: Loading...")
        
        self.all_models = await self.ollama_service.list_local_models()
        self.filtered_models = self.all_models.copy()
        
        model_list = self.query_one("#model-list", ModelList)
        model_list.update_models(self.filtered_models)
        
        count_label = self.query_one("#count-label", Label)
        count_label.update(f"Models: {len(self.filtered_models)}")
        
        status_label.update("Status: Ready")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        if event.input.id == "filter-input":
            filter_text = event.value.lower()
            
            if not filter_text:
                self.filtered_models = self.all_models.copy()
            else:
                self.filtered_models = [
                    model for model in self.all_models
                    if filter_text in model.name.lower()
                ]
            
            model_list = self.query_one("#model-list", ModelList)
            model_list.update_models(self.filtered_models)
            
            count_label = self.query_one("#count-label", Label)
            count_label.update(f"Models: {len(self.filtered_models)}")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-button":
            await self.action_refresh_models()
        elif event.button.id == "delete-button":
            await self.action_delete_model()
    
    async def action_refresh_models(self) -> None:
        """Action to refresh models."""
        await self.refresh_models()
    
    async def action_delete_model(self) -> None:
        """Action to delete selected model."""
        model_list = self.query_one("#model-list", ModelList)
        selected_model = model_list.get_selected_model()
        
        if selected_model:
            status_label = self.query_one("#status-label", Label)
            status_label.update(f"Status: Deleting {selected_model}...")
            
            success = await self.ollama_service.delete_model(selected_model)
            
            if success:
                status_label.update(f"Status: Deleted {selected_model}")
                await self.refresh_models()
            else:
                status_label.update(f"Status: Failed to delete {selected_model}")
    
    def action_copy_to_chat(self) -> None:
        """Action to copy selected model to chat."""
        model_list = self.query_one("#model-list", ModelList)
        selected_model = model_list.get_selected_model()
        
        if selected_model:
            # Post message to app to switch to chat with this model
            self.post_message(self.ModelSelected(selected_model))