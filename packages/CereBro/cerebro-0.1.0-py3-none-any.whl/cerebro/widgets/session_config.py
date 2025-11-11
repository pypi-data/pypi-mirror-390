"""Session configuration panel widget."""

from textual.widgets import Static, Label, Select, Input
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from typing import Optional, List


class SessionConfig(Vertical):
    """Widget for session configuration."""
    
    DEFAULT_CSS = """
    SessionConfig {
        width: 35;
        border: solid $primary;
        padding: 1 2;
        background: $surface;
    }
    
    SessionConfig > Label {
        margin-bottom: 1;
        text-style: bold;
        color: $accent;
    }
    
    SessionConfig Input {
        width: 1fr;
        margin-bottom: 1;
    }
    
    SessionConfig Select {
        width: 1fr;
        margin-bottom: 1;
    }
    
    .config-section {
        height: auto;
        margin-bottom: 2;
    }
    
    .config-label {
        color: $text;
        margin-bottom: 1;
        text-style: bold;
    }
    
    .setting-group {
        margin-bottom: 2;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_models: List[str] = []
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label("⚙ Session Config")
        
        # Model selection
        with Vertical(classes="setting-group"):
            yield Label("Model", classes="config-label")
            yield Select(
                options=[("No models available", "")],
                id="model-select",
                allow_blank=True
            )
        
        # Temperature
        with Vertical(classes="setting-group"):
            yield Label("Temperature", classes="config-label")
            yield Input(
                value="0.7",
                id="temperature-input",
                type="number",
                placeholder="0.0 - 2.0"
            )
        
        # Max Tokens
        with Vertical(classes="setting-group"):
            yield Label("Max Tokens", classes="config-label")
            yield Input(
                value="2048",
                id="max-tokens-input",
                type="number",
                placeholder="e.g., 2048"
            )
        
        # System Prompt
        with Vertical(classes="setting-group"):
            yield Label("System Prompt", classes="config-label")
            yield Input(
                placeholder="Optional system prompt...",
                id="system-prompt-input"
            )
    
    def update_models(self, models: List[str]) -> None:
        """Update available models."""
        self.available_models = models
        select = self.query_one("#model-select", Select)
        
        if models:
            select.set_options([(model, model) for model in models])
            # Select the first model by default
            if len(models) > 0:
                select.value = models[0]
        else:
            select.set_options([("No models available", "")])
    
    def get_config(self) -> dict:
        """Get current configuration."""
        model_select = self.query_one("#model-select", Select)
        temp_input = self.query_one("#temperature-input", Input)
        tokens_input = self.query_one("#max-tokens-input", Input)
        system_input = self.query_one("#system-prompt-input", Input)
        
        return {
            "model": str(model_select.value) if model_select.value else "",
            "temperature": float(temp_input.value or 0.7),
            "max_tokens": int(tokens_input.value or 2048),
            "system_prompt": system_input.value or None
        }
    
    def set_config(self, config: dict) -> None:
        """Set configuration values."""
        if "model" in config:
            model_select = self.query_one("#model-select", Select)
            model_select.value = config["model"]
        
        if "temperature" in config:
            temp_input = self.query_one("#temperature-input", Input)
            temp_input.value = str(config["temperature"])
        
        if "max_tokens" in config:
            tokens_input = self.query_one("#max-tokens-input", Input)
            tokens_input.value = str(config["max_tokens"])
        
        if "system_prompt" in config and config["system_prompt"]:
            system_input = self.query_one("#system-prompt-input", Input)
            system_input.value = config["system_prompt"]