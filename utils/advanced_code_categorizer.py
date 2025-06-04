"""
Advanced Code Categorization Module

This module provides enhanced code categorization using advanced techniques
including machine learning-inspired heuristics and pattern recognition.
"""

import re
import os
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter

class AdvancedCodeCategorizer:
    """Advanced code categorization using sophisticated heuristics and pattern recognition."""
    
    def __init__(self):
        """Initialize the advanced code categorizer."""
        # Define category keywords with weights
        self.category_keywords = {
            "data_analysis": {
                "high": ["pandas", "numpy", "matplotlib", "seaborn", "dataframe", "plot", "visualization"],
                "medium": ["data", "analysis", "statistics", "csv", "excel", "chart", "graph"],
                "low": ["series", "column", "row", "figure", "axis"]
            },
            "web_development": {
                "high": ["flask", "django", "fastapi", "http", "request", "response", "api"],
                "medium": ["html", "css", "javascript", "route", "endpoint", "server", "client"],
                "low": ["get", "post", "template", "static", "render"]
            },
            "machine_learning": {
                "high": ["sklearn", "tensorflow", "keras", "pytorch", "model", "train", "predict"],
                "medium": ["classifier", "regression", "neural", "network", "accuracy", "precision", "recall"],
                "low": ["feature", "label", "dataset", "batch", "epoch"]
            },
            "automation": {
                "high": ["selenium", "beautifulsoup", "scrape", "automate", "schedule", "cron", "task"],
                "medium": ["browser", "headless", "parse", "extract", "collect", "periodic"],
                "low": ["click", "fill", "submit", "download"]
            },
            "database": {
                "high": ["sql", "sqlite", "mysql", "postgresql", "mongodb", "query", "database"],
                "medium": ["table", "schema", "index", "join", "select", "insert", "update"],
                "low": ["record", "field", "column", "row", "primary", "foreign", "key"]
            },
            "file_processing": {
                "high": ["file", "open", "read", "write", "json", "csv", "xml"],
                "medium": ["path", "directory", "folder", "parse", "format", "encode", "decode"],
                "low": ["line", "content", "text", "binary", "stream"]
            },
            "algorithms": {
                "high": ["algorithm", "sort", "search", "graph", "tree", "recursion", "dynamic"],
                "medium": ["complexity", "optimization", "efficient", "performance", "structure"],
                "low": ["iterate", "traverse", "compute", "calculate"]
            },
            "system": {
                "high": ["os", "system", "process", "thread", "subprocess", "command", "shell"],
                "medium": ["environment", "variable", "path", "platform", "service", "daemon"],
                "low": ["execute", "run", "terminate", "kill", "status"]
            },
            "networking": {
                "high": ["socket", "http", "tcp", "udp", "ip", "request", "response"],
                "medium": ["client", "server", "protocol", "packet", "connection", "url"],
                "low": ["port", "host", "domain", "address", "send", "receive"]
            },
            "gui": {
                "high": ["tkinter", "pyqt", "pyside", "kivy", "gui", "widget", "window"],
                "medium": ["button", "label", "frame", "canvas", "event", "interface"],
                "low": ["click", "display", "show", "hide", "layout"]
            }
        }
        
        # Define import patterns for better categorization
        self.import_patterns = {
            "data_analysis": [
                r"import\s+(pandas|numpy|matplotlib|seaborn|plotly)",
                r"from\s+(pandas|numpy|matplotlib|seaborn|plotly)(\.\w+)?\s+import"
            ],
            "web_development": [
                r"import\s+(flask|django|fastapi|requests|aiohttp|tornado|bottle)",
                r"from\s+(flask|django|fastapi|requests|aiohttp|tornado|bottle)(\.\w+)?\s+import"
            ],
            "machine_learning": [
                r"import\s+(sklearn|tensorflow|keras|torch|xgboost)",
                r"from\s+(sklearn|tensorflow|keras|torch|xgboost)(\.\w+)?\s+import"
            ],
            "automation": [
                r"import\s+(selenium|bs4|scrapy|schedule)",
                r"from\s+(selenium|bs4|scrapy|schedule)(\.\w+)?\s+import"
            ],
            "database": [
                r"import\s+(sqlite3|mysql|psycopg2|pymongo|sqlalchemy)",
                r"from\s+(sqlite3|mysql|psycopg2|pymongo|sqlalchemy)(\.\w+)?\s+import"
            ],
            "system": [
                r"import\s+(os|sys|subprocess|platform|shutil)",
                r"from\s+(os|sys|subprocess|platform|shutil)(\.\w+)?\s+import"
            ],
            "networking": [
                r"import\s+(socket|http|urllib|requests)",
                r"from\s+(socket|http|urllib|requests)(\.\w+)?\s+import"
            ],
            "gui": [
                r"import\s+(tkinter|PyQt5|PySide2|kivy)",
                r"from\s+(tkinter|PyQt5|PySide2|kivy)(\.\w+)?\s+import"
            ]
        }
        
        # Define code structure patterns
        self.structure_patterns = {
            "data_analysis": [
                r"\.plot\(",
                r"\.DataFrame\(",
                r"\.read_csv\(",
                r"\.read_excel\("
            ],
            "web_development": [
                r"@app\.route\(",
                r"@app\.get\(",
                r"@app\.post\(",
                r"Flask\(__name__\)",
                r"render_template\("
            ],
            "machine_learning": [
                r"\.fit\(",
                r"\.predict\(",
                r"train_test_split\(",
                r"\.compile\(",
                r"\.evaluate\("
            ],
            "automation": [
                r"\.find_element\(",
                r"\.click\(\)",
                r"\.send_keys\(",
                r"BeautifulSoup\("
            ],
            "database": [
                r"\.execute\(",
                r"\.cursor\(\)",
                r"\.commit\(\)",
                r"\.connect\("
            ]
        }
        
        # Initialize learning history
        self.category_history = Counter()
    
    def categorize(self, code: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Categorize code using advanced heuristics and pattern recognition.
        
        Args:
            code: The Python code to categorize
            
        Returns:
            Tuple containing (category, confidence, category_scores)
        """
        # Normalize code
        normalized_code = self._normalize_code(code)
        
        # Calculate scores for each category
        category_scores = {}
        
        # Check for imports (strongest signal)
        import_scores = self._analyze_imports(normalized_code)
        
        # Check for structure patterns
        structure_scores = self._analyze_structure(normalized_code)
        
        # Check for keywords
        keyword_scores = self._analyze_keywords(normalized_code)
        
        # Combine scores with different weights
        for category in self.category_keywords.keys():
            # Import signals are strongest
            import_weight = 3.0
            # Structure patterns are strong signals
            structure_weight = 2.0
            # Keywords are weaker signals
            keyword_weight = 1.0
            
            # Calculate weighted score
            category_scores[category] = (
                import_weight * import_scores.get(category, 0) +
                structure_weight * structure_scores.get(category, 0) +
                keyword_weight * keyword_scores.get(category, 0)
            )
        
        # Apply history bias (slight preference for previously seen categories)
        for category, count in self.category_history.items():
            if category in category_scores:
                # Add a small bias based on history (max 20% boost)
                history_boost = min(0.2, count / (sum(self.category_history.values()) + 1))
                category_scores[category] *= (1 + history_boost)
        
        # Get best category and confidence
        if not category_scores:
            return "general", 0.0, {"general": 1.0}
        
        best_category = max(category_scores, key=category_scores.get)
        
        # Calculate confidence (normalize scores)
        total_score = sum(category_scores.values())
        if total_score > 0:
            normalized_scores = {k: v/total_score for k, v in category_scores.items()}
            confidence = normalized_scores[best_category]
        else:
            normalized_scores = {k: 0 for k in category_scores}
            confidence = 0.0
        
        # Update history
        self.category_history[best_category] += 1
        
        return best_category, confidence, normalized_scores
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code by removing comments and extra whitespace."""
        # Remove single-line comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line strings and comments (simplified approach)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        return code
    
    def _analyze_imports(self, code: str) -> Dict[str, float]:
        """Analyze imports in the code to determine category."""
        scores = {}
        
        for category, patterns in self.import_patterns.items():
            category_score = 0
            for pattern in patterns:
                matches = re.findall(pattern, code)
                category_score += len(matches)
            
            if category_score > 0:
                scores[category] = category_score
        
        # Normalize scores
        total = sum(scores.values()) if scores else 1
        return {k: v/total for k, v in scores.items()}
    
    def _analyze_structure(self, code: str) -> Dict[str, float]:
        """Analyze code structure patterns to determine category."""
        scores = {}
        
        for category, patterns in self.structure_patterns.items():
            category_score = 0
            for pattern in patterns:
                matches = re.findall(pattern, code)
                category_score += len(matches)
            
            if category_score > 0:
                scores[category] = category_score
        
        # Normalize scores
        total = sum(scores.values()) if scores else 1
        return {k: v/total for k, v in scores.items()}
    
    def _analyze_keywords(self, code: str) -> Dict[str, float]:
        """Analyze keywords in the code to determine category."""
        scores = {}
        
        # Convert code to lowercase for case-insensitive matching
        code_lower = code.lower()
        
        for category, keyword_groups in self.category_keywords.items():
            category_score = 0
            
            # Check high-weight keywords (weight: 3)
            for keyword in keyword_groups["high"]:
                count = code_lower.count(keyword.lower())
                category_score += count * 3
            
            # Check medium-weight keywords (weight: 2)
            for keyword in keyword_groups["medium"]:
                count = code_lower.count(keyword.lower())
                category_score += count * 2
            
            # Check low-weight keywords (weight: 1)
            for keyword in keyword_groups["low"]:
                count = code_lower.count(keyword.lower())
                category_score += count
            
            if category_score > 0:
                scores[category] = category_score
        
        # Normalize scores
        total = sum(scores.values()) if scores else 1
        return {k: v/total for k, v in scores.items()}
    
    def get_category_suggestions(self, code: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Get top N category suggestions with confidence scores.
        
        Args:
            code: The Python code to categorize
            top_n: Number of top categories to return
            
        Returns:
            List of tuples containing (category, confidence)
        """
        _, _, scores = self.categorize(code)
        
        # Sort categories by score in descending order
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N categories
        return sorted_categories[:top_n]
