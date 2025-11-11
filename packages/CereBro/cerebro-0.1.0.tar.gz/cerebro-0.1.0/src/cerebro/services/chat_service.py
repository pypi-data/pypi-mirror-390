"""Service for managing chat sessions."""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
from cerebro.models import ChatSession, Message


class ChatService:
    """Service for chat session management."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".local" / "share" / "parllama-minimal"
        
        self.data_dir = data_dir
        self.sessions_dir = data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(
        self,
        model: str,
        name: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        if name is None:
            name = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = ChatSession(
            id=session_id,
            name=name,
            model=model,
            system_prompt=system_prompt
        )
        
        self.save_session(session)
        return session
    
    def save_session(self, session: ChatSession) -> None:
        """Save a chat session to disk."""
        session.updated_at = datetime.now()
        session_file = self.sessions_dir / f"{session.id}.json"
        
        with open(session_file, "w") as f:
            json.dump(session.model_dump(mode="json"), f, indent=2, default=str)
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load a chat session from disk."""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
                return ChatSession(**data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[ChatSession]:
        """List all saved sessions."""
        sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    sessions.append(ChatSession(**data))
            except Exception as e:
                print(f"Error loading session {session_file}: {e}")
        
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        try:
            if session_file.exists():
                session_file.unlink()
                return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
        
        return False
    
    def add_message(self, session: ChatSession, role: str, content: str) -> None:
        """Add a message to a session."""
        message = Message(role=role, content=content)
        session.messages.append(message)
        self.save_session(session)
    
    def export_session_markdown(self, session: ChatSession) -> str:
        """Export session to markdown format."""
        md_lines = [
            f"# {session.name}",
            f"\n**Model:** {session.model}",
            f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Temperature:** {session.temperature}",
            "\n---\n"
        ]
        
        if session.system_prompt:
            md_lines.append(f"\n## System Prompt\n\n{session.system_prompt}\n")
        
        md_lines.append("\n## Conversation\n")
        
        for msg in session.messages:
            role_label = msg.role.capitalize()
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            md_lines.append(f"\n### {role_label} ({timestamp})\n\n{msg.content}\n")
        
        return "\n".join(md_lines)