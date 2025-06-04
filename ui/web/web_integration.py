"""
Integration module for connecting the web interface with backend logic.

This module provides the necessary functions to integrate the web UI with
the backend components of the Python Bot.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, session
import uuid

class WebIntegration:
    """Handles integration between web UI and backend components."""
    
    def __init__(self, app, config_manager, conversation_manager, advanced_context_manager, 
                 api_client, code_executor, code_manager, code_categorizer):
        """
        Initialize web integration with all necessary components.
        
        Args:
            app: Flask application instance
            config_manager: Configuration manager instance
            conversation_manager: Conversation manager instance
            advanced_context_manager: Advanced context manager instance
            api_client: API client instance
            code_executor: Code executor instance
            code_manager: Code manager instance
            code_categorizer: Code categorizer instance
        """
        self.app = app
        self.config_manager = config_manager
        self.conversation_manager = conversation_manager
        self.advanced_context_manager = advanced_context_manager
        self.api_client = api_client
        self.code_executor = code_executor
        self.code_manager = code_manager
        self.code_categorizer = code_categorizer
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes for API endpoints."""
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Handle chat API endpoint."""
            data = request.json
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({'error': 'No message provided'}), 400
            
            # Initialize session if needed
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            # Add user message to conversation managers
            self.conversation_manager.add_message("user", user_message)
            self.advanced_context_manager.add_message("user", user_message)
            
            # Get optimized context for API request
            context = self.advanced_context_manager.get_optimized_context()
            
            # Get response from API
            response = self.api_client.get_completion(context)
            
            # Add assistant response to conversation managers
            self.conversation_manager.add_message("assistant", response)
            self.advanced_context_manager.add_message("assistant", response)
            
            # Check if response contains code
            code_snippets = []
            if self.code_manager.detect_code(response):
                code = self.code_manager.extract_code(response)
                if code:
                    code_snippets.append(code)
                    
                    # Categorize code if present
                    if code:
                        category, confidence, _ = self.code_categorizer.categorize(code)
                        code_info = {
                            'code': code,
                            'category': category,
                            'confidence': confidence
                        }
                        code_snippets = [code_info]
            
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
            category = None
            if success and self.config_manager.get("app", "auto_save_code", True):
                # Use advanced categorization
                category, confidence, _ = self.code_categorizer.categorize(code)
                if confidence < 0.5:
                    category = "general"
                    
                saved_path = self.code_manager.save_code(code, category)
            
            return jsonify({
                'output': output,
                'error': error,
                'success': success,
                'saved_path': saved_path,
                'category': category
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
            self.advanced_context_manager = self.advanced_context_manager.__class__()
            return jsonify({'success': True})
        
        @self.app.route('/api/categorize', methods=['POST'])
        def categorize_code():
            """Categorize code snippet."""
            data = request.json
            code = data.get('code', '')
            
            if not code:
                return jsonify({'error': 'No code provided'}), 400
            
            # Get category suggestions
            suggestions = self.code_categorizer.get_category_suggestions(code, top_n=3)
            
            return jsonify({
                'suggestions': [
                    {'category': category, 'confidence': confidence}
                    for category, confidence in suggestions
                ]
            })
        
        @self.app.route('/api/context', methods=['POST'])
        def get_relevant_context():
            """Get context relevant to a query."""
            data = request.json
            query = data.get('query', '')
            
            if not query:
                return jsonify({'error': 'No query provided'}), 400
            
            # Get relevant context
            context = self.advanced_context_manager.get_relevant_context(query)
            
            return jsonify({'context': context})
