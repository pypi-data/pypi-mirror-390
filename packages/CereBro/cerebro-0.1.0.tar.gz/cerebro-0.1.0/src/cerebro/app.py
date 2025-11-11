"""Main application class."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.binding import Binding
from cerebro.screens.chat_screen import ChatScreen
from cerebro.screens.local_models_screen import LocalModelsScreen
from cerebro.screens.site_models_screen import SiteModelsScreen
from cerebro.services.ollama_service import OllamaService
from cerebro.services.chat_service import ChatService


class CereBroApp(App):
    """Main  application."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    TabbedContent {
        height: 1fr;
    }
    
    TabPane {
        padding: 1;
    }
    
    #main-container {
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__()
        self.title = "CereBro"
        self.ollama_service = OllamaService(ollama_url)
        self.chat_service = ChatService()
        self.current_session = None
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        
        with TabbedContent(initial="chat"):
            with TabPane("Chat", id="chat"):
                yield ChatScreen(
                    ollama_service=self.ollama_service,
                    chat_service=self.chat_service
                )
            
            with TabPane("Local", id="local"):
                yield LocalModelsScreen(ollama_service=self.ollama_service)
            
            with TabPane("Site", id="site"):
                yield SiteModelsScreen()
        
        yield Footer()
    
    def action_new_chat(self) -> None:
        """Create a new chat session."""
        # Switch to chat tab and create new session
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "chat"
        
        chat_screen = self.query_one(ChatScreen)
        chat_screen.new_session()
    
    def action_refresh(self) -> None:
        """Refresh current screen data."""
        tabbed_content = self.query_one(TabbedContent)
        active_pane = tabbed_content.active
        
        if active_pane == "local":
            local_screen = self.query_one(LocalModelsScreen)
            local_screen.refresh_models()
        elif active_pane == "site":
            site_screen = self.query_one(SiteModelsScreen)
            site_screen.refresh_models()
    
    async def on_mount(self) -> None:
        """Handle mount event."""
        # Load initial data
        pass
    
    async def on_unmount(self) -> None:
        """Handle unmount event."""
        await self.ollama_service.close()