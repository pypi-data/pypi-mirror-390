"""Chat panel widget for displaying messages."""

from textual.widgets import RichLog, Static
from textual.containers import VerticalScroll, Vertical
from textual.app import ComposeResult
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from cerebro.models import Message, ChatSession
from typing import List, Optional
from datetime import datetime


class ChatPanel(Vertical):
    """Widget for displaying chat messages."""
    
    DEFAULT_CSS = """
    ChatPanel {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }
    
    ChatPanel RichLog {
        height: 1fr;
        background: $surface;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.streaming_content = ""
        self.is_streaming = False
        self.all_messages: List[Message] = []
        self.streaming_start_time = None
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield RichLog(
            highlight=True,
            markup=True,
            id="chat-log",
            auto_scroll=True
        )
    
    def clear(self) -> None:
        """Clear all messages."""
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        self.streaming_content = ""
        self.is_streaming = False
        self.all_messages.clear()
    
    def add_message(self, message: Message) -> None:
        """Add a message to the chat display."""
        self.all_messages.append(message)
        self._render_message(message)
    
    def _render_message(self, message: Message) -> None:
        """Render a single message to the log."""
        log = self.query_one("#chat-log", RichLog)
        
        # Format timestamp
        timestamp = message.timestamp.strftime("%H:%M:%S")
        
        # Create styled panel based on role
        if message.role == "user":
            style = "blue"
            title = f"[bold]You[/bold] ({timestamp})"
        elif message.role == "assistant":
            style = "green"
            title = f"[bold]Assistant[/bold] ({timestamp})"
        else:
            style = "yellow"
            title = f"[bold]System[/bold] ({timestamp})"
        
        # Render markdown content
        md = Markdown(message.content)
        panel = Panel(
            md,
            title=title,
            border_style=style,
            expand=False
        )
        
        log.write(panel)
        log.write("")  # Add spacing
    
    def start_streaming_message(self) -> None:
        """Start a new streaming message."""
        self.streaming_content = ""
        self.is_streaming = True
        self.streaming_start_time = datetime.now()
        
        log = self.query_one("#chat-log", RichLog)
        
        # Add initial streaming indicator
        panel = Panel(
            Text("● Generating...", style="dim italic"),
            title="[bold green]Assistant[/bold green]",
            border_style="green",
            expand=False
        )
        log.write(panel)
    
    def update_streaming_message(self, content: str) -> None:
        """Update the streaming message content."""
        if not self.is_streaming:
            return
        
        self.streaming_content = content
        log = self.query_one("#chat-log", RichLog)
        
        # Clear and re-render everything
        log.clear()
        
        # Re-render all previous messages
        for msg in self.all_messages:
            self._render_message(msg)
        
        # Render the streaming content
        if content:
            md = Markdown(content)
            timestamp = self.streaming_start_time.strftime("%H:%M:%S") if self.streaming_start_time else ""
            panel = Panel(
                md,
                title=f"[bold green]Assistant[/bold green] ({timestamp}) [dim italic]streaming...[/dim italic]",
                border_style="green",
                expand=False
            )
            log.write(panel)
    
    def finalize_streaming_message(self) -> None:
        """Finalize the streaming message."""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        # Add the final streamed message to all_messages
        if self.streaming_content:
            final_msg = Message(
                role="assistant",
                content=self.streaming_content,
                timestamp=self.streaming_start_time or datetime.now()
            )
            self.all_messages.append(final_msg)
        
        # Clear and re-render everything one final time
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        
        for msg in self.all_messages:
            self._render_message(msg)
        
        self.streaming_content = ""
    
    def load_session(self, session: ChatSession) -> None:
        """Load a session's messages."""
        self.clear()
        
        # Add system prompt if exists
        if session.system_prompt:
            system_msg = Message(
                role="system",
                content=session.system_prompt,
                timestamp=session.created_at
            )
            self.add_message(system_msg)
        
        # Add all messages
        for message in session.messages:
            self.add_message(message)