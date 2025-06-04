"""
Conversation Management Module

This module manages conversation history and context for the chatbot.
"""

import re
import json
from typing import List, Dict, Any, Optional

class ConversationManager:
    """Manages conversation history and context for the chatbot."""
    
    def __init__(self, max_turns: int = 10):
        """Initialize conversation manager with specified maximum turns."""
        self.max_turns = max_turns
        self.messages = []
        self.code_snippets = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        
        # Extract code snippets from assistant messages
        if role == "assistant" and self._contains_code(content):
            code = self._extract_code(content)
            if code:
                self.code_snippets.append(code)
        
        # Trim conversation if it exceeds max turns
        if len(self.messages) > self.max_turns * 2:  # Each turn has user + assistant message
            self.messages = self.messages[-self.max_turns * 2:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation history."""
        return self.messages
    
    def get_code_snippets(self) -> List[str]:
        """Get all code snippets from the conversation."""
        return self.code_snippets
    
    def get_latest_code(self) -> Optional[str]:
        """Get the most recent code snippet."""
        return self.code_snippets[-1] if self.code_snippets else None
    
    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages = []
        self.code_snippets = []
    
    def _contains_code(self, text: str) -> bool:
        """Check if text contains code blocks."""
        return bool(re.search(r"```python(.*?)```", text, re.DOTALL))
    
    def _extract_code(self, text: str) -> Optional[str]:
        """Extract code from markdown code blocks."""
        code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        return None
    
    def export_to_file(self, filename: str) -> bool:
        """Export conversation history to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2)
            return True
        except Exception:
            # Fallback to ASCII encoding if UTF-8 fails
            try:
                with open(filename, 'w', encoding='ascii', errors='replace') as f:
                    json.dump(self.messages, f, indent=2)
                return True
            except Exception:
                return False
    
    def import_from_file(self, filename: str) -> bool:
        """Import conversation history from a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        except UnicodeDecodeError:
            # Fallback to ASCII encoding if UTF-8 fails
            try:
                with open(filename, 'r', encoding='ascii', errors='replace') as f:
                    self.messages = json.load(f)
            except Exception:
                return False
                
        # Rebuild code snippets
        self.code_snippets = []
        for msg in self.messages:
            if msg["role"] == "assistant" and self._contains_code(msg["content"]):
                code = self._extract_code(msg["content"])
                if code:
                    self.code_snippets.append(code)
        
        return True
