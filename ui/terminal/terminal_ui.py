"""
Terminal UI Module

This module provides a terminal-based user interface for the chatbot.
"""

import os
import time
from typing import Callable, Optional

# Try importing optional dependencies with fallbacks
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    try:
        from termcolor import cprint, colored
    except ImportError:
        def cprint(text, color=None, **kwargs):
            print(text)
        def colored(text, color=None, **kwargs):
            return text

class TerminalUI:
    """Provides a terminal-based user interface for the chatbot."""
    
    def __init__(self, config_manager):
        """Initialize terminal UI with configuration manager."""
        self.config_manager = config_manager
        self.use_rich = RICH_AVAILABLE and self.config_manager.get("ui", "use_rich_ui", True)
        
        if self.use_rich:
            self.console = Console()
        
        self.bot_name = self.config_manager.get("ui", "bot_name", "Advanced Python Assistant")
        self.primary_color = self.config_manager.get("ui", "primary_color", "cyan")
        self.secondary_color = self.config_manager.get("ui", "secondary_color", "green")
        self.error_color = self.config_manager.get("ui", "error_color", "red")
        self.success_color = self.config_manager.get("ui", "success_color", "magenta")
    
    def display_welcome(self):
        """Display welcome message."""
        if self.use_rich:
            self.console.print(f"[bold {self.primary_color}]{self.bot_name}[/bold {self.primary_color}]")
            self.console.print("[dim]Type your Python questions or 'exit' to quit.[/dim]")
        else:
            cprint(self.bot_name, self.primary_color, attrs=['bold'])
            print("Type your Python questions or 'exit' to quit.")
    
    def display_message(self, message: str, is_user: bool = False):
        """Display a message in the terminal."""
        if is_user:
            prefix = "You: "
            color = self.secondary_color
        else:
            prefix = f"{self.bot_name}: "
            color = self.primary_color
        
        if self.use_rich:
            self.console.print(f"[bold {color}]{prefix}[/bold {color}]", end="")
            
            # Check if message contains code blocks for special formatting
            if "```python" in message and "```" in message:
                # Split by code blocks
                parts = message.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Regular text
                        if part.strip():
                            self.console.print(part)
                    else:  # Code block
                        if part.startswith("python"):
                            code = part[6:].strip()  # Remove "python" prefix
                        else:
                            code = part.strip()
                        
                        if code:
                            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
                            self.console.print(Panel(syntax))
            else:
                # Regular message without code blocks
                self.console.print(message)
        else:
            print(colored(prefix, color, attrs=['bold']), end="")
            print(message)
    
    def display_code_execution_result(self, output: str, error: str, success: bool):
        """Display code execution result."""
        if output:
            if self.use_rich:
                self.console.print("\n[bold]Output:[/bold]")
                self.console.print(Panel(output))
            else:
                print("\nOutput:")
                print(output)
        
        if error:
            color = self.error_color
            if self.use_rich:
                self.console.print(f"\n[bold {color}]Error:[/bold {color}]")
                self.console.print(Panel(error, style=f"on {color}"))
            else:
                print(colored("\nError:", color, attrs=['bold']))
                print(colored(error, color))
        
        if success and not error:
            if self.use_rich:
                self.console.print(f"\n[{self.success_color}]Code executed successfully![/{self.success_color}]")
            else:
                cprint("\nCode executed successfully!", self.success_color)
    
    def get_user_input(self) -> str:
        """Get input from the user."""
        if self.use_rich:
            self.console.print(f"\n[bold {self.secondary_color}]You:[/bold {self.secondary_color}] ", end="")
            return input()
        else:
            return input(colored("\nYou: ", self.secondary_color, attrs=['bold']))
    
    def display_thinking(self, callback: Optional[Callable] = None):
        """
        Display a thinking animation while waiting for a response.
        
        Args:
            callback: Optional function to call while thinking animation is running
        """
        if self.use_rich:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Thinking...[/bold blue]"),
                transient=True,
            ) as progress:
                task = progress.add_task("Thinking...", total=None)
                
                # If callback is provided, call it
                if callback:
                    callback()
                else:
                    # Otherwise, just wait a bit for visual effect
                    time.sleep(2)
        else:
            print("Thinking...")
            
            # If callback is provided, call it
            if callback:
                callback()
            else:
                # Otherwise, just wait a bit for visual effect
                time.sleep(2)
    
    def display_error(self, message: str):
        """Display an error message."""
        if self.use_rich:
            self.console.print(f"[bold {self.error_color}]Error:[/bold {self.error_color}] {message}")
        else:
            cprint(f"Error: {message}", self.error_color)
    
    def display_success(self, message: str):
        """Display a success message."""
        if self.use_rich:
            self.console.print(f"[bold {self.success_color}]{message}[/bold {self.success_color}]")
        else:
            cprint(message, self.success_color)
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
