"""
Conversation Service for DDMA (d²media Agent)

Manages multi-turn conversations, session history, and context window management
for the DDMA conversational AI agent.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class ConversationService:
    """
    Service for managing conversational history and sessions
    
    Features:
    - Session creation and management
    - Message history storage
    - Context window management
    - Message pruning for long conversations
    - Conversation metadata tracking
    """
    
    def __init__(self, max_context_tokens: int = 8192):
        """
        Initialize conversation service
        
        Args:
            max_context_tokens: Maximum tokens in context window
        """
        self.max_context_tokens = max_context_tokens
        # In production, use database instead of dict
        self.sessions = {}
    
    async def create_session(
        self,
        user_id: Optional[int] = None,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new conversation session
        
        Args:
            user_id: User identifier
            system_prompt: Custom system prompt
            metadata: Additional metadata
            
        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "messages": [],
            "system_prompt": system_prompt,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "token_count": 0,
            "message_count": 0
        }
        
        # Add system prompt as first message if provided
        if system_prompt:
            await self.add_message(session_id, "system", system_prompt)
        
        return session_id
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Add a message to conversation history
        
        Args:
            session_id: Session ID
            role: Message role (system, user, assistant, tool)
            content: Message content
            metadata: Additional metadata
            
        Returns:
            Message object
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "token_count": len(content.split()) * 1.3  # Approximate
        }
        
        session = self.sessions[session_id]
        session["messages"].append(message)
        session["updated_at"] = datetime.now()
        session["message_count"] += 1
        session["token_count"] += message["token_count"]
        
        # Prune if exceeding context window
        if session["token_count"] > self.max_context_tokens:
            await self.prune_conversation(session_id)
        
        return message
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        include_system: bool = True
    ) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages to return
            include_system: Include system messages
            
        Returns:
            List of messages
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        messages = self.sessions[session_id]["messages"]
        
        if not include_system:
            messages = [msg for msg in messages if msg["role"] != "system"]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    async def prune_conversation(self, session_id: str) -> int:
        """
        Prune conversation to fit within context window
        
        Strategy:
        - Keep system prompt
        - Keep recent messages
        - Remove older messages from middle
        
        Args:
            session_id: Session ID
            
        Returns:
            Number of messages removed
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        messages = session["messages"]
        
        if session["token_count"] <= self.max_context_tokens:
            return 0
        
        # Keep system prompt (first message if system)
        system_messages = []
        other_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_messages.append(msg)
            else:
                other_messages.append(msg)
        
        # Calculate how many recent messages to keep
        target_tokens = self.max_context_tokens * 0.8  # Keep 80% capacity
        system_tokens = sum(msg["token_count"] for msg in system_messages)
        available_tokens = target_tokens - system_tokens
        
        # Keep recent messages
        kept_messages = system_messages.copy()
        current_tokens = system_tokens
        
        for msg in reversed(other_messages):
            if current_tokens + msg["token_count"] <= available_tokens:
                kept_messages.insert(len(system_messages), msg)
                current_tokens += msg["token_count"]
            else:
                break
        
        messages_removed = len(messages) - len(kept_messages)
        
        session["messages"] = kept_messages
        session["token_count"] = current_tokens
        session["message_count"] = len(kept_messages)
        
        return messages_removed
    
    async def get_session_info(self, session_id: str) -> Dict:
        """
        Get session information
        
        Args:
            session_id: Session ID
            
        Returns:
            Session information
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session["session_id"],
            "user_id": session["user_id"],
            "message_count": session["message_count"],
            "token_count": session["token_count"],
            "created_at": session["created_at"].isoformat(),
            "updated_at": session["updated_at"].isoformat(),
            "metadata": session["metadata"]
        }
    
    async def list_sessions(
        self,
        user_id: Optional[int] = None,
        active_since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        List conversation sessions
        
        Args:
            user_id: Filter by user ID
            active_since: Filter by activity since datetime
            
        Returns:
            List of session information
        """
        sessions = []
        
        for session in self.sessions.values():
            # Apply filters
            if user_id and session["user_id"] != user_id:
                continue
            
            if active_since and session["updated_at"] < active_since:
                continue
            
            sessions.append({
                "session_id": session["session_id"],
                "user_id": session["user_id"],
                "message_count": session["message_count"],
                "created_at": session["created_at"].isoformat(),
                "updated_at": session["updated_at"].isoformat()
            })
        
        # Sort by most recent first
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        
        return sessions
    
    async def end_session(self, session_id: str) -> bool:
        """
        End a conversation session
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session was ended
        """
        if session_id in self.sessions:
            # In production, archive to database before deleting
            del self.sessions[session_id]
            return True
        return False
    
    async def clear_old_sessions(self, days: int = 30) -> int:
        """
        Clear sessions older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of sessions cleared
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session["updated_at"] < cutoff_date:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        return len(sessions_to_remove)
    
    async def export_conversation(
        self,
        session_id: str,
        format: str = "json"
    ) -> str:
        """
        Export conversation history
        
        Args:
            session_id: Session ID
            format: Export format (json, text)
            
        Returns:
            Exported conversation string
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        messages = session["messages"]
        
        if format == "json":
            return json.dumps({
                "session_id": session_id,
                "created_at": session["created_at"].isoformat(),
                "messages": messages
            }, indent=2)
        elif format == "text":
            lines = [f"Conversation: {session_id}"]
            lines.append(f"Created: {session['created_at']}")
            lines.append("-" * 50)
            
            for msg in messages:
                role = msg["role"].upper()
                content = msg["content"]
                timestamp = msg["timestamp"]
                lines.append(f"\n[{timestamp}] {role}:")
                lines.append(content)
            
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
