import unittest
from conversation.advanced_context_manager import AdvancedContextManager

class TestAdvancedContextManager(unittest.TestCase):
    """Test cases for the AdvancedContextManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.context_manager = AdvancedContextManager(max_context_length=2000, max_messages=10)
    
    def test_add_message(self):
        """Test adding messages to context."""
        # Add user message
        user_msg_id = self.context_manager.add_message("user", "Can you help me with pandas DataFrame filtering?")
        
        # Add assistant message
        assistant_msg_id = self.context_manager.add_message("assistant", 
            "Sure! Here's an example of filtering a DataFrame:\n```python\nimport pandas as pd\ndf = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})\nfiltered = df[df['A'] > 1]\nprint(filtered)\n```")
        
        # Check if messages were added correctly
        self.assertEqual(len(self.context_manager.messages), 2)
        self.assertEqual(user_msg_id, 0)
        self.assertEqual(assistant_msg_id, 1)
        
        # Check if topic was detected correctly
        self.assertEqual(self.context_manager.messages[0]["topic"], "data_analysis")
        
        # Check if code was extracted correctly
        self.assertTrue("code_snippets" in self.context_manager.messages[1])
        self.assertTrue("import pandas as pd" in self.context_manager.messages[1]["code_snippets"][0])
    
    def test_get_optimized_context(self):
        """Test getting optimized context."""
        # Add several messages
        self.context_manager.add_message("system", "You are a helpful Python assistant.")
        self.context_manager.add_message("user", "How do I read a CSV file?")
        self.context_manager.add_message("assistant", "You can use pandas:\n```python\nimport pandas as pd\ndf = pd.read_csv('file.csv')\n```")
        self.context_manager.add_message("user", "How do I filter rows?")
        self.context_manager.add_message("assistant", "You can use boolean indexing:\n```python\nfiltered_df = df[df['column'] > value]\n```")
        
        # Get optimized context
        context = self.context_manager.get_optimized_context()
        
        # Check if context is in correct format
        self.assertEqual(len(context), 5)
        self.assertEqual(context[0]["role"], "system")
        self.assertEqual(context[1]["role"], "user")
        self.assertEqual(context[2]["role"], "assistant")
        
        # Check if context is sorted correctly
        roles = [msg["role"] for msg in context]
        self.assertEqual(roles, ["system", "user", "assistant", "user", "assistant"])
    
    def test_get_relevant_context(self):
        """Test getting context relevant to a query."""
        # Add several messages on different topics
        self.context_manager.add_message("user", "How do I create a Flask app?")
        self.context_manager.add_message("assistant", "Here's how to create a basic Flask app:\n```python\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello, World!'\n\nif __name__ == '__main__':\n    app.run(debug=True)\n```")
        
        self.context_manager.add_message("user", "How do I analyze data with pandas?")
        self.context_manager.add_message("assistant", "Here's a pandas example:\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\nsummary = df.describe()\nprint(summary)\n```")
        
        self.context_manager.add_message("user", "How do I create a neural network?")
        self.context_manager.add_message("assistant", "Here's a simple neural network with TensorFlow:\n```python\nimport tensorflow as tf\nmodel = tf.keras.Sequential([\n    tf.keras.layers.Dense(128, activation='relu'),\n    tf.keras.layers.Dense(10, activation='softmax')\n])\n```")
        
        # Get context relevant to pandas query
        pandas_context = self.context_manager.get_relevant_context("How do I filter data in pandas?")
        
        # Check if pandas-related messages are included
        pandas_content = " ".join([msg["content"] for msg in pandas_context])
        self.assertTrue("pandas" in pandas_content)
        self.assertTrue("df" in pandas_content)
        
        # Get context relevant to Flask query
        flask_context = self.context_manager.get_relevant_context("How do I add routes to Flask?")
        
        # Check if Flask-related messages are included
        flask_content = " ".join([msg["content"] for msg in flask_context])
        self.assertTrue("Flask" in flask_content)
        self.assertTrue("app.route" in flask_content)
    
    def test_context_optimization(self):
        """Test context optimization when exceeding limits."""
        # Add more messages than max_messages
        for i in range(15):
            self.context_manager.add_message("user", f"User message {i}")
            self.context_manager.add_message("assistant", f"Assistant message {i}")
        
        # Check if context was optimized
        self.assertLessEqual(len(self.context_manager.messages), self.context_manager.max_messages)
        
        # Check if recent messages were kept
        messages = self.context_manager.messages
        last_message = messages[-1]
        self.assertEqual(last_message["content"], "Assistant message 14")

if __name__ == '__main__':
    unittest.main()
