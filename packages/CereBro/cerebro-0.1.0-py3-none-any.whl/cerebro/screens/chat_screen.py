"""Chat screen for conversations with LLMs."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container, VerticalScroll
from textual.widgets import Input, Button, Label, Static, Select
from textual.binding import Binding
from textual.worker import Worker, WorkerState
from rich.text import Text
from cerebro.widgets.chat_panel import ChatPanel
from cerebro.widgets.session_config import SessionConfig
from cerebro.services.ollama_service import OllamaService
from cerebro.services.chat_service import ChatService
from cerebro.models import ChatSession, Message
from typing import Optional, List
import asyncio


from textual.message import Message as TextualMessage

class SessionItem(Static):
    """A clickable session item."""
    
    DEFAULT_CSS = """
    SessionItem {
        padding: 1;
        background: $surface;
        margin-bottom: 1;
        border-left: solid $primary;
        height: auto;
    }
    
    SessionItem:hover {
        background: $primary 20%
    }
    
    SessionItem.selected {
        background: $primary 30%;
        border-left: heavy $primary;
    }
    """
    
    class Selected(TextualMessage):
        """Message when session is selected."""
        def __init__(self, session: ChatSession, widget: "SessionItem"):
            super().__init__()
            self.session = session
            self.widget = widget
    
    def __init__(self, session: ChatSession, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
    
    def render(self) -> Text:
        """Render the session item."""
        msg_count = len(self.session.messages)
        updated = self.session.updated_at.strftime("%m/%d %H:%M")
        
        text = Text()
        text.append(self.session.name, style="bold")
        text.append("\n")
        text.append(f"{self.session.model} • {msg_count} msgs • {updated}", style="dim")
        return text
    
    def on_click(self) -> None:
        """Handle click event."""
        self.post_message(self.Selected(self.session, self))

class ChatScreen(Vertical):
    """Screen for chatting with LLMs."""
    
    DEFAULT_CSS = """
    ChatScreen {
        height: 1fr;
    }
    
    #main-chat-container {
        height: 1fr;
    }
    
    #sessions-sidebar {
        width: 30;
        border-right: heavy $primary;
        background: $panel;
        padding: 1;
    }
    
    #sessions-sidebar.hidden {
        display: none;
    }
    
    #sidebar-header {
        height: auto;
        margin-bottom: 1;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    
    #sidebar-title {
        text-style: bold;
        color: $primary;
        text-align: center;
    }
    
    #sessions-scroll {
        height: 1fr;
        background: $panel;
        border: solid $primary 30%;
    }
    
    #chat-area {
        width: 1fr;
    }
    
    #input-container {
        height: 5;
        padding: 1;
        background: $surface;
        border-top: solid $primary;
    }
    
    #message-input {
        width: 1fr;
    }
    
    #session-info {
        height: 4;
        padding: 1 2;
        background: $panel;
        border-bottom: solid $primary;
    }
    
    #session-info Label {
        margin-bottom: 1;
    }
    
    #session-name-label {
        text-style: bold;
        color: $accent;
    }
    
    #session-stats-label {
        color: $text-muted;
    }
    
    .action-button {
        margin-left: 1;
        min-width: 8;
    }
    
    #sidebar-buttons {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+n", "new_session", "New Session"),
        Binding("ctrl+s", "save_session", "Save"),
        Binding("ctrl+e", "export_session", "Export"),
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+d", "delete_session", "Delete Session"),
        Binding("enter", "send_message", "Send", key_display="Enter"),
    ]
    
    def __init__(
        self,
        ollama_service: OllamaService,
        chat_service: ChatService,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.ollama_service = ollama_service
        self.chat_service = chat_service
        self.current_session: Optional[ChatSession] = None
        self.is_generating = False
        self.generation_worker: Optional[Worker] = None
        self.sessions: List[ChatSession] = []
        self.sidebar_visible = True
        self.selected_session_item: Optional[SessionItem] = None
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        with Vertical(id="session-info"):
            yield Label("No active session", id="session-name-label")
            yield Label("Model: None | Temp: 0.7 | Messages: 0", id="session-stats-label")
        
        with Horizontal(id="main-chat-container"):
            # Sessions sidebar
            with Vertical(id="sessions-sidebar"):
                with Vertical(id="sidebar-header"):
                    yield Label("💬 Recent Sessions", id="sidebar-title")
                
                yield VerticalScroll(id="sessions-scroll")
                
                with Horizontal(id="sidebar-buttons"):
                    yield Button("New", variant="success", classes="action-button", id="new-session-btn")
                    yield Button("Delete", variant="error", classes="action-button", id="delete-session-btn")
            
            with Vertical(id="chat-area"):
                yield ChatPanel(id="chat-panel")
            
            yield SessionConfig(id="session-config")
        
        with Horizontal(id="input-container"):
            yield Input(
                placeholder="Type a message... (use /help for commands)",
                id="message-input"
            )
            yield Button("Send", id="send-button", variant="primary", classes="action-button")
            yield Button("Stop", id="stop-button", variant="error", classes="action-button", disabled=True)
    
    async def on_mount(self) -> None:
        """Handle mount event."""
        # Load available models
        models = await self.ollama_service.list_local_models()
        model_names = [m.name for m in models]
        
        session_config = self.query_one("#session-config", SessionConfig)
        session_config.update_models(model_names)
        
        # Load sessions
        self.refresh_sessions_list()
        
        # Create initial session if models available
        if model_names:
            self.new_session()
    
    def refresh_sessions_list(self) -> None:
        """Refresh the sessions list in the sidebar."""
        self.sessions = self.chat_service.list_sessions()
        sessions_scroll = self.query_one("#sessions-scroll", VerticalScroll)
        
        # Clear existing items
        sessions_scroll.remove_children()
        
        # Add session items
        for session in self.sessions:
            item = SessionItem(session)
            sessions_scroll.mount(item)

    async def auto_name_session(self, first_message: str) -> None:
        """Automatically name the session based on the first message."""
        if not self.current_session:
            return
        
        try:
            # Create a prompt to generate a short session name
            naming_prompt = f"""Based on this question, generate a very short (2-5 word) descriptive title. 
    Only respond with the title, nothing else.

    Question: {first_message}

    Title:"""
            
            # Use the same model to generate the name
            full_response = ""
            async for chunk in self.ollama_service.chat(
                model=self.current_session.model,
                messages=[{"role": "user", "content": naming_prompt}],
                temperature=0.7
            ):
                full_response += chunk
            
            # Clean up the response
            session_name = full_response.strip().strip('"').strip("'")
            
            # Limit length
            if len(session_name) > 50:
                session_name = session_name[:50] + "..."
            
            # Update session name
            if session_name and session_name != self.current_session.name:
                self.current_session.name = session_name
                self.chat_service.save_session(self.current_session)
                self.update_session_info()
                self.refresh_sessions_list()
        
        except Exception as e:
            # If naming fails, just keep the default name
            print(f"Failed to auto-name session: {e}")
    
    def on_session_item_selected(self, event: SessionItem.Selected) -> None:
        """Handle session item selection."""
        # Deselect previous item
        if self.selected_session_item:
            self.selected_session_item.remove_class("selected")
        
        # Select new item
        event.widget.add_class("selected")
        self.selected_session_item = event.widget
        
        # Load the session
        self.load_session(event.session)
        
    def load_session(self, session: ChatSession) -> None:
        """Load a session."""
        self.current_session = session
        
        # Update config panel
        session_config = self.query_one("#session-config", SessionConfig)
        session_config.set_config({
            "model": session.model,
            "temperature": session.temperature,
            "max_tokens": session.max_tokens,
            "system_prompt": session.system_prompt
        })
        
        # Load messages
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        chat_panel.load_session(session)
        
        self.update_session_info()
    
    def new_session(self) -> None:
        """Create a new chat session."""
        session_config = self.query_one("#session-config", SessionConfig)
        config = session_config.get_config()
        
        if not config["model"]:
            return
        
        self.current_session = self.chat_service.create_session(
            model=config["model"],
            system_prompt=config.get("system_prompt")
        )
        
        self.current_session.temperature = config["temperature"]
        self.current_session.max_tokens = config["max_tokens"]
        
        # Update UI
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        chat_panel.clear()
        
        self.update_session_info()
        self.refresh_sessions_list()
    
    def update_session_info(self) -> None:
        """Update session info display."""
        if not self.current_session:
            return
        
        name_label = self.query_one("#session-name-label", Label)
        name_label.update(f"Session: {self.current_session.name}")
        
        stats_label = self.query_one("#session-stats-label", Label)
        message_count = len(self.current_session.messages)
        stats_label.update(
            f"Model: {self.current_session.model} | "
            f"Temp: {self.current_session.temperature} | "
            f"Messages: {message_count}"
        )
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "send-button":
            await self.action_send_message()
        elif event.button.id == "stop-button":
            self.action_stop_generation()
        elif event.button.id == "new-session-btn":
            self.action_new_session()
        elif event.button.id == "delete-session-btn":
            self.action_delete_session()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "message-input":
            await self.action_send_message()
    
    async def stream_response(self, api_messages: list) -> None:
        """Stream response from LLM."""
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        
        # Start streaming indicator
        chat_panel.start_streaming_message()
        
        assistant_content = ""
        try:
            async for chunk in self.ollama_service.chat(
                model=self.current_session.model,
                messages=api_messages,
                temperature=self.current_session.temperature
            ):
                if not self.is_generating:
                    break
                
                assistant_content += chunk
                # Update the streaming message in real-time
                chat_panel.update_streaming_message(assistant_content)
                
                # Small delay to prevent UI freezing
                await asyncio.sleep(0.01)
            
            # Finalize the message
            if assistant_content:
                assistant_msg = Message(role="assistant", content=assistant_content)
                self.current_session.messages.append(assistant_msg)
                chat_panel.finalize_streaming_message()
                
                # Save session
                self.chat_service.save_session(self.current_session)
                self.update_session_info()
                self.refresh_sessions_list()
        
        except Exception as e:
            error_content = f"Error: {str(e)}"
            chat_panel.update_streaming_message(error_content)
            chat_panel.finalize_streaming_message()
    
    async def action_send_message(self) -> None:
        """Action to send a message."""
        if not self.current_session or self.is_generating:
            return
        
        message_input = self.query_one("#message-input", Input)
        user_message = message_input.value.strip()
        
        if not user_message:
            return
        
        # Handle slash commands
        if user_message.startswith("/"):
            self.handle_slash_command(user_message)
            message_input.value = ""
            return
        
        # Clear input
        message_input.value = ""
        
        # Add user message
        user_msg = Message(role="user", content=user_message)
        self.current_session.messages.append(user_msg)
        
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        chat_panel.add_message(user_msg)

        # Auto-name session if this is the first user message
        user_message_count = sum(1 for msg in self.current_session.messages if msg.role == "user")
        should_auto_name = user_message_count == 1  # First user message
        
        # Generate response
        self.is_generating = True
        self.toggle_input_state(False)
        
        # Prepare messages for API
        api_messages = []
        if self.current_session.system_prompt:
            api_messages.append({
                "role": "system",
                "content": self.current_session.system_prompt
            })
        
        for msg in self.current_session.messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Run streaming in worker
        self.generation_worker = self.run_worker(
            self.stream_response(api_messages),
            exclusive=True
        )
        
        # Auto-name session in background if it's the first message
        if should_auto_name:
            self.run_worker(self.auto_name_session(user_message), exclusive=False)
    
    def toggle_input_state(self, enabled: bool) -> None:
        """Toggle input controls."""
        message_input = self.query_one("#message-input", Input)
        send_button = self.query_one("#send-button", Button)
        stop_button = self.query_one("#stop-button", Button)
        
        message_input.disabled = not enabled
        send_button.disabled = not enabled
        stop_button.disabled = enabled
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.worker == self.generation_worker:
            if event.state in (WorkerState.SUCCESS, WorkerState.ERROR, WorkerState.CANCELLED):
                self.is_generating = False
                self.toggle_input_state(True)
    
    def handle_slash_command(self, command: str) -> None:
        """Handle slash commands."""
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        
        if command == "/help" or command == "/?":
            help_text = """
Available commands:
- /help or /? - Show this help
- /clear - Clear current chat
- /export - Export chat to markdown
- /new - Create new session
"""
            help_msg = Message(role="system", content=help_text)
            chat_panel.add_message(help_msg)
        
        elif command == "/clear":
            if self.current_session:
                self.current_session.messages.clear()
                chat_panel.clear()
                self.chat_service.save_session(self.current_session)
        
        elif command == "/export":
            self.action_export_session()
        
        elif command == "/new":
            self.new_session()
    
    def action_new_session(self) -> None:
        """Action to create new session."""
        self.new_session()
    
    def action_save_session(self) -> None:
        """Action to save session."""
        if self.current_session:
            self.chat_service.save_session(self.current_session)
            self.refresh_sessions_list()
            
            chat_panel = self.query_one("#chat-panel", ChatPanel)
            msg = Message(role="system", content="Session saved!")
            chat_panel.add_message(msg)
    
    def action_delete_session(self) -> None:
        """Delete the currently selected session."""
        if not self.selected_session_item:
            return
        
        session_to_delete = self.selected_session_item.session
        
        # Delete from service
        self.chat_service.delete_session(session_to_delete.id)
        
        # If it's the current session, clear it
        if self.current_session and self.current_session.id == session_to_delete.id:
            self.current_session = None
            chat_panel = self.query_one("#chat-panel", ChatPanel)
            chat_panel.clear()
            
            name_label = self.query_one("#session-name-label", Label)
            name_label.update("No active session")
        
        # Clear selection
        self.selected_session_item = None
        
        # Refresh list
        self.refresh_sessions_list()
    
    def action_export_session(self) -> None:
        """Action to export session."""
        if not self.current_session:
            return
        
        markdown = self.chat_service.export_session_markdown(self.current_session)
        
        # Save to file
        from pathlib import Path
        export_dir = Path.home() / "Downloads"
        export_dir.mkdir(exist_ok=True)
        
        filename = f"{self.current_session.name.replace(' ', '_')}.md"
        filepath = export_dir / filename
        
        with open(filepath, "w") as f:
            f.write(markdown)
        
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        msg = Message(role="system", content=f"Exported to {filepath}")
        chat_panel.add_message(msg)
    
    def action_stop_generation(self) -> None:
        """Action to stop generation."""
        self.is_generating = False
        if self.generation_worker:
            self.generation_worker.cancel()
        self.toggle_input_state(True)
    
    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sessions-sidebar")
        if self.sidebar_visible:
            sidebar.add_class("hidden")
        else:
            sidebar.remove_class("hidden")
        self.sidebar_visible = not self.sidebar_visible