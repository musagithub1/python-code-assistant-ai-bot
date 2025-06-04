"""
Main application entry point for the Python Bot Upgraded.

This module integrates all components and provides the main application functionality.
"""

import os
import argparse
from config.config_manager import ConfigManager
from conversation.conversation_manager import ConversationManager
from conversation.advanced_context_manager import AdvancedContextManager
from code_execution.code_executor import CodeExecutor
from api.api_client import APIClient
from utils.code_manager import CodeManager
from utils.advanced_code_categorizer import AdvancedCodeCategorizer
from ui.terminal.terminal_ui import TerminalUI
from ui.web.web_ui import WebUI

def main(args=None):
    """Main entry point for the application."""
    # Parse command-line arguments
    if args is None:
        parser = argparse.ArgumentParser(description='Advanced Python Code Assistant Bot')
        parser.add_argument('--web', action='store_true', help='Start web interface')
        parser.add_argument('--port', type=int, default=5000, help='Port for web interface')
        parser.add_argument('--config', type=str, default='config.ini', help='Path to config file')
        args = parser.parse_args()
    
    # Initialize components
    config_manager = ConfigManager(args.config)
    conversation_manager = ConversationManager(
        max_turns=int(config_manager.get("app", "max_conversation_turns", 10))
    )
    advanced_context_manager = AdvancedContextManager()
    code_executor = CodeExecutor(
        timeout=int(config_manager.get("app", "code_execution_timeout", 5))
    )
    api_client = APIClient(config_manager)
    code_manager = CodeManager(
        save_folder=config_manager.get("app", "save_folder", "bot_outputs")
    )
    code_categorizer = AdvancedCodeCategorizer()
    
    # Start appropriate interface
    if args.web:
        # Start web interface
        web_ui = WebUI(
            config_manager=config_manager,
            conversation_manager=conversation_manager,
            api_client=api_client,
            code_executor=code_executor,
            code_manager=code_manager
        )
        web_ui.run(host='0.0.0.0', port=args.port, debug=False)
    else:
        # Start terminal interface
        terminal_ui = TerminalUI(config_manager)
        run_terminal_interface(
            terminal_ui=terminal_ui,
            conversation_manager=conversation_manager,
            advanced_context_manager=advanced_context_manager,
            api_client=api_client,
            code_executor=code_executor,
            code_manager=code_manager,
            code_categorizer=code_categorizer
        )

def run_terminal_interface(terminal_ui, conversation_manager, advanced_context_manager, 
                          api_client, code_executor, code_manager, code_categorizer):
    """Run the terminal interface."""
    terminal_ui.display_welcome()
    
    while True:
        # Get user input
        user_input = terminal_ui.get_user_input()
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'bye']:
            terminal_ui.display_message("Goodbye! Have a great day.", is_user=False)
            break
        
        # Add user message to conversation
        conversation_manager.add_message("user", user_input)
        advanced_context_manager.add_message("user", user_input)
        
        # Display thinking animation and get response from API
        def get_response():
            # Get optimized context
            context = advanced_context_manager.get_optimized_context()
            
            # Get response from API
            return api_client.get_completion(context)
        
        terminal_ui.display_thinking(get_response)
        
        # Get response
        context = advanced_context_manager.get_optimized_context()
        response = api_client.get_completion(context)
        
        # Add assistant message to conversation
        conversation_manager.add_message("assistant", response)
        advanced_context_manager.add_message("assistant", response)
        
        # Display response
        terminal_ui.display_message(response, is_user=False)
        
        # Check if response contains code
        if code_manager.detect_code(response):
            code = code_manager.extract_code(response)
            if code:
                # Ask if user wants to execute the code
                terminal_ui.display_message("Would you like to execute this code? (y/n)", is_user=False)
                execute_input = terminal_ui.get_user_input()
                
                if execute_input.lower() in ['y', 'yes']:
                    # Execute code
                    output, error, success = code_executor.execute_code(code)
                    
                    # Display results
                    terminal_ui.display_code_execution_result(output, error, success)
                    
                    # Save code if successful
                    if success:
                        # Use advanced categorization
                        category, confidence, _ = code_categorizer.get_category_suggestions(code)[0]
                        if confidence < 0.5:
                            category = "general"
                            
                        file_path = code_manager.save_code(code, category)
                        terminal_ui.display_success(f"Code saved to {file_path}")

if __name__ == '__main__':
    main()
