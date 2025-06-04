"""
Web UI Module - Flask Application

This module provides a web-based user interface for the chatbot.
"""

from flask import Flask, render_template, request, jsonify, session
import os
import uuid
from typing import Dict, Any

class WebUI:
    """Provides a web-based user interface for the chatbot."""
    
    def __init__(self, config_manager, conversation_manager, api_client, code_executor, code_manager):
        """Initialize web UI with required components."""
        self.config_manager = config_manager
        self.conversation_manager = conversation_manager
        self.api_client = api_client
        self.code_executor = code_executor
        self.code_manager = code_manager
        
        # Initialize Flask app
        self.app = Flask(__name__, 
                         template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                         static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        self.app.secret_key = os.urandom(24)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes."""
        
        @self.app.route('/')
        def index():
            """Render the main page."""
            # Initialize session if needed
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            bot_name = self.config_manager.get("ui", "bot_name", "Advanced Python Assistant")
            return render_template('index.html', bot_name=bot_name)
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Handle chat API endpoint."""
            data = request.json
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({'error': 'No message provided'}), 400
            
            # Add user message to conversation
            self.conversation_manager.add_message("user", user_message)
            
            # Get response from API
            messages = self.conversation_manager.get_messages()
            response = self.api_client.get_completion(messages)
            
            # Add assistant response to conversation
            self.conversation_manager.add_message("assistant", response)
            
            # Check if response contains code
            code_snippets = []
            if self.code_manager.detect_code(response):
                code = self.code_manager.extract_code(response)
                if code:
                    code_snippets.append(code)
            
            return jsonify({
                'response': response,
                'code_snippets': code_snippets
            })
        
        @self.app.route('/api/execute', methods=['POST'])
        def execute_code():
            """Handle code execution API endpoint."""
            data = request.json
            code = data.get('code', '')
            
            if not code:
                return jsonify({'error': 'No code provided'}), 400
            
            # Execute code
            output, error, success = self.code_executor.execute_code(code)
            
            # Save code if successful and auto-save is enabled
            saved_path = None
            if success and self.config_manager.get("app", "auto_save_code", True):
                category = self.code_manager.categorize_code(code)
                saved_path = self.code_manager.save_code(code, category)
            
            return jsonify({
                'output': output,
                'error': error,
                'success': success,
                'saved_path': saved_path
            })
        
        @self.app.route('/api/history', methods=['GET'])
        def get_history():
            """Get conversation history."""
            messages = self.conversation_manager.get_messages()
            return jsonify({'messages': messages})
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear_history():
            """Clear conversation history."""
            self.conversation_manager.clear()
            return jsonify({'success': True})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application."""
        self.app.run(host=host, port=port, debug=debug)
