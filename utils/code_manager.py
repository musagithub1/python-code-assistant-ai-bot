"""
Code Management Module

This module manages code detection, saving, and organization.
"""

import os
import re
import datetime
from typing import Optional

class CodeManager:
    """Manages code detection, saving, and organization."""
    
    def __init__(self, save_folder: str = "bot_outputs"):
        """Initialize code manager with specified save folder."""
        self.save_folder = save_folder
        os.makedirs(save_folder, exist_ok=True)
    
    def detect_code(self, text: str) -> bool:
        """
        Advanced code detection using multiple patterns and heuristics.
        """
        # Check for code blocks first
        if re.search(r"```python(.*?)```", text, re.DOTALL):
            return True
        
        # Check for common Python patterns
        patterns = [
            r"def\s+\w+\s*\(",  # Function definition
            r"class\s+\w+\s*(\(.*?\))?:",  # Class definition
            r"import\s+[\w\.]+",  # Import statement
            r"from\s+[\w\.]+\s+import",  # From import statement
            r"if\s+.+:",  # If statement
            r"for\s+.+:",  # For loop
            r"while\s+.+:",  # While loop
            r"try:",  # Try block
            r"except\s+",  # Except block
            r"def\s+\w+\s*\([^)]\)\s->",  # Type-annotated function
            r"@\w+",  # Decorator
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        # Check if the text has multiple lines with Python-like indentation
        lines = text.split('\n')
        indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
        if indented_lines > 2 and indented_lines / len(lines) > 0.3:
            return True
        
        return False
    
    def extract_code(self, text: str) -> str:
        """Extract code from text, handling markdown code blocks."""
        # Try to extract from markdown code blocks first
        code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        
        # If no code blocks, try to extract based on indentation and patterns
        lines = text.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            # Check for code-like patterns
            if re.match(r"(def\s+\w+|class\s+\w+|import\s+|from\s+.+\s+import|if\s+.+:|for\s+.+:|while\s+.+:)", line.strip()):
                in_code_block = True
                code_lines.append(line)
            # Check for indented lines (part of code block)
            elif line.startswith('    ') or line.startswith('\t'):
                if in_code_block:
                    code_lines.append(line)
            # Empty lines within code blocks are kept
            elif line.strip() == '' and in_code_block:
                code_lines.append(line)
            # Other lines might end the code block
            else:
                in_code_block = False
        
        return '\n'.join(code_lines)
    
    def save_code(self, code: str, category: str = "general") -> str:
        """Save code to a file with timestamp and category."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        category_folder = os.path.join(self.save_folder, category)
        os.makedirs(category_folder, exist_ok=True)
        
        filename = f"{category_folder}/code_{timestamp}.py"
        
        try:
            with open(filename, "w", encoding='utf-8') as f:
                f.write(code)
        except UnicodeEncodeError:
            # Fallback to ASCII encoding if UTF-8 fails
            with open(filename, "w", encoding='ascii', errors='replace') as f:
                f.write(code)
        
        return filename
    
    def categorize_code(self, code: str) -> str:
        """Attempt to categorize code based on content analysis."""
        categories = {
            "data_analysis": ["pandas", "numpy", "matplotlib", "seaborn", "data", "dataframe", "plot"],
            "web": ["flask", "django", "fastapi", "html", "http", "request", "api"],
            "ml": ["sklearn", "tensorflow", "keras", "model", "train", "predict"],
            "utility": ["util", "helper", "tool", "function"],
            "database": ["sql", "database", "query", "sqlite", "mysql", "postgresql"],
            "file_io": ["file", "open", "read", "write", "csv", "json", "load", "save"],
        }
        
        # Default category
        best_category = "general"
        best_score = 0
        
        # Check each category
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword.lower() in code.lower())
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
