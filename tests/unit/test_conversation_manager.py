import unittest
import tempfile
import os
import json
from conversation.conversation_manager import ConversationManager

class TestConversationManager(unittest.TestCase):
    """Test cases for the ConversationManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.conversation_manager = ConversationManager(max_turns=5)
    
    def test_add_message(self):
        """Test adding messages to conversation."""
        # Add user message
        self.conversation_manager.add_message("user", "Hello, can you help me with Python?")
        
        # Add assistant message with code
        self.conversation_manager.add_message(
            "assistant", 
            "Sure! Here's a simple example:\n```python\nprint('Hello, world!')\n```"
        )
        
        # Check if messages were added correctly
        messages = self.conversation_manager.get_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")
    
    def test_get_code_snippets(self):
        """Test extracting code snippets from conversation."""
        # Add assistant message with code
        self.conversation_manager.add_message(
            "assistant", 
            "Here's a simple example:\n```python\nprint('Hello, world!')\n```"
        )
        
        # Add another assistant message with code
        self.conversation_manager.add_message(
            "assistant", 
            "And here's another example:\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n```"
        )
        
        # Check if code snippets were extracted correctly
        snippets = self.conversation_manager.get_code_snippets()
        self.assertEqual(len(snippets), 2)
        self.assertEqual(snippets[0], "print('Hello, world!')")
        self.assertTrue("def greet(name):" in snippets[1])
    
    def test_get_latest_code(self):
        """Test getting the latest code snippet."""
        # Add assistant message with code
        self.conversation_manager.add_message(
            "assistant", 
            "First example:\n```python\nprint('First')\n```"
        )
        
        # Add another assistant message with code
        self.conversation_manager.add_message(
            "assistant", 
            "Second example:\n```python\nprint('Second')\n```"
        )
        
        # Check if latest code snippet is correct
        latest_code = self.conversation_manager.get_latest_code()
        self.assertEqual(latest_code, "print('Second')")
    
    def test_clear(self):
        """Test clearing conversation history."""
        # Add some messages
        self.conversation_manager.add_message("user", "Hello")
        self.conversation_manager.add_message("assistant", "Hi there!")
        
        # Clear conversation
        self.conversation_manager.clear()
        
        # Check if conversation was cleared
        self.assertEqual(len(self.conversation_manager.get_messages()), 0)
        self.assertEqual(len(self.conversation_manager.get_code_snippets()), 0)
    
    def test_max_turns_limit(self):
        """Test that conversation is limited to max_turns."""
        # Add more messages than max_turns
        for i in range(12):  # 6 turns (user + assistant)
            self.conversation_manager.add_message("user", f"User message {i}")
            self.conversation_manager.add_message("assistant", f"Assistant message {i}")
        
        # Check if conversation was limited to max_turns
        messages = self.conversation_manager.get_messages()
        self.assertEqual(len(messages), 10)  # 5 turns * 2 messages
        
        # Check if oldest messages were removed
        self.assertEqual(messages[0]["content"], "User message 7")
    
    def test_export_import(self):
        """Test exporting and importing conversation history."""
        # Add some messages
        self.conversation_manager.add_message("user", "Hello")
        self.conversation_manager.add_message(
            "assistant", 
            "Hi! Here's some code:\n```python\nprint('Test')\n```"
        )
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            filename = temp_file.name
        
        try:
            # Export conversation
            success = self.conversation_manager.export_to_file(filename)
            self.assertTrue(success)
            
            # Create new conversation manager
            new_manager = ConversationManager()
            
            # Import conversation
            success = new_manager.import_from_file(filename)
            self.assertTrue(success)
            
            # Check if messages were imported correctly
            imported_messages = new_manager.get_messages()
            self.assertEqual(len(imported_messages), 2)
            self.assertEqual(imported_messages[0]["role"], "user")
            self.assertEqual(imported_messages[0]["content"], "Hello")
            
            # Check if code snippets were rebuilt
            imported_snippets = new_manager.get_code_snippets()
            self.assertEqual(len(imported_snippets), 1)
            self.assertEqual(imported_snippets[0], "print('Test')")
            
        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)

if __name__ == '__main__':
    unittest.main()
