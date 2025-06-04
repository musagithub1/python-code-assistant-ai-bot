"""
Code Execution Module

This module provides a sandboxed environment for executing Python code.
"""

import io
import sys
import ast
import signal
import traceback
import contextlib
from typing import Tuple

class CodeExecutor:
    """Provides a sandboxed environment for executing Python code."""
    
    def __init__(self, timeout: int = 5):
        """Initialize code executor with specified timeout."""
        self.timeout = timeout
        # Check if we're on Windows
        self.is_windows = sys.platform.startswith('win')
    
    def execute_code(self, code: str) -> Tuple[str, str, bool]:
        """
        Execute Python code in a sandboxed environment.
        
        Returns:
            Tuple containing (output, error_message, success_flag)
        """
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Prepare restricted globals
        restricted_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in dir(__builtins__)
                if name not in ['open', 'exec', 'eval', 'compile', '__import__']
            }
        }
        
        success = True
        
        try:
            # Validate syntax first
            ast.parse(code)
            
            if self.is_windows:
                # Windows doesn't support SIGALRM, use a different approach
                # Execute code with captured output
                with contextlib.redirect_stdout(stdout_capture):
                    with contextlib.redirect_stderr(stderr_capture):
                        exec(code, restricted_globals)
            else:
                # Set up timeout handler for Unix systems
                def timeout_handler(signum, frame):
                    raise TimeoutError("Code execution timed out")
                
                # Set timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout)
                
                # Execute code with captured output
                with contextlib.redirect_stdout(stdout_capture):
                    with contextlib.redirect_stderr(stderr_capture):
                        exec(code, restricted_globals)
                
                # Reset alarm
                signal.alarm(0)
            
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
        except SyntaxError as e:
            success = False
            output = ""
            error = f"Syntax Error: {str(e)}"
        except TimeoutError as e:
            success = False
            output = stdout_capture.getvalue()
            error = f"Execution Timeout: Code took too long to run (> {self.timeout}s)"
        except Exception as e:
            success = False
            output = stdout_capture.getvalue()
            error = f"Error: {str(e)}\n{traceback.format_exc()}"
        
        return output, error, success
