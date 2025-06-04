"""
Advanced Context Management Module

This module provides enhanced conversation context management with
sophisticated context tracking, relevance scoring, and memory optimization.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
import json
import datetime

class AdvancedContextManager:
    """Advanced conversation context management with sophisticated tracking and optimization."""
    
    def __init__(self, max_context_length: int = 4000, max_messages: int = 20):
        """
        Initialize the advanced context manager.
        
        Args:
            max_context_length: Maximum total context length in tokens (approximate)
            max_messages: Maximum number of messages to retain
        """
        self.max_context_length = max_context_length
        self.max_messages = max_messages
        self.messages = []
        self.message_importance = {}  # Maps message index to importance score
        self.topics = {}  # Topic tracking
        self.current_topic = None
        self.code_references = {}  # Track code references across conversation
        self.last_optimization = datetime.datetime.now()
    
    def add_message(self, role: str, content: str) -> int:
        """
        Add a message to the conversation context with advanced processing.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            
        Returns:
            Index of the added message
        """
        # Create message object with metadata
        message_id = len(self.messages)
        timestamp = datetime.datetime.now().isoformat()
        
        message = {
            "id": message_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "tokens": self._estimate_tokens(content)
        }
        
        # Extract entities and keywords
        entities, keywords = self._extract_entities_and_keywords(content)
        message["entities"] = entities
        message["keywords"] = keywords
        
        # Extract code if present
        code_snippets = self._extract_code(content)
        if code_snippets:
            message["code_snippets"] = code_snippets
            
            # Update code references
            for snippet in code_snippets:
                snippet_hash = hash(snippet)
                self.code_references[snippet_hash] = message_id
        
        # Detect topic
        detected_topic = self._detect_topic(content, keywords)
        message["topic"] = detected_topic
        
        # Update current topic if this is a user message
        if role == "user":
            self.current_topic = detected_topic
        
        # Update topic tracking
        if detected_topic not in self.topics:
            self.topics[detected_topic] = []
        self.topics[detected_topic].append(message_id)
        
        # Calculate initial importance score
        importance = self._calculate_importance(message, role)
        self.message_importance[message_id] = importance
        
        # Add message to conversation
        self.messages.append(message)
        
        # Optimize context if needed
        self._optimize_context_if_needed()
        
        return message_id
    
    def get_optimized_context(self, max_length: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get optimized conversation context for API requests.
        
        Args:
            max_length: Optional maximum context length override
            
        Returns:
            List of message dictionaries with role and content
        """
        if max_length is None:
            max_length = self.max_context_length
        
        # Always include system message if present
        context = []
        system_messages = [m for m in self.messages if m["role"] == "system"]
        if system_messages:
            context.extend(system_messages)
        
        # Get remaining context budget
        used_tokens = sum(m["tokens"] for m in context)
        remaining_tokens = max_length - used_tokens
        
        # Get non-system messages sorted by importance
        regular_messages = [m for m in self.messages if m["role"] != "system"]
        
        # Always include the most recent messages
        recent_count = min(4, len(regular_messages))
        recent_messages = regular_messages[-recent_count:]
        regular_messages = regular_messages[:-recent_count]
        
        # Add recent messages to context
        for msg in recent_messages:
            context.append(msg)
            used_tokens += msg["tokens"]
            remaining_tokens = max_length - used_tokens
        
        # Sort remaining messages by importance
        sorted_messages = sorted(
            regular_messages,
            key=lambda m: self.message_importance.get(m["id"], 0),
            reverse=True
        )
        
        # Add important messages until we reach the limit
        for msg in sorted_messages:
            if msg["tokens"] <= remaining_tokens:
                context.append(msg)
                used_tokens += msg["tokens"]
                remaining_tokens = max_length - used_tokens
            
            if remaining_tokens <= 0:
                break
        
        # Sort messages by original order
        context.sort(key=lambda m: m["id"])
        
        # Convert to simple format for API
        return [{"role": m["role"], "content": m["content"]} for m in context]
    
    def get_relevant_context(self, query: str, max_messages: int = 5) -> List[Dict[str, str]]:
        """
        Get context most relevant to a specific query.
        
        Args:
            query: The query to find relevant context for
            max_messages: Maximum number of messages to return
            
        Returns:
            List of relevant message dictionaries
        """
        # Extract entities and keywords from query
        query_entities, query_keywords = self._extract_entities_and_keywords(query)
        
        # Score messages by relevance to query
        relevance_scores = {}
        
        for msg in self.messages:
            score = 0
            
            # Score based on keyword overlap
            msg_keywords = set(msg.get("keywords", []))
            keyword_overlap = msg_keywords.intersection(query_keywords)
            score += len(keyword_overlap) * 2
            
            # Score based on entity overlap
            msg_entities = set(msg.get("entities", []))
            entity_overlap = msg_entities.intersection(query_entities)
            score += len(entity_overlap) * 3
            
            # Score based on topic match
            query_topic = self._detect_topic(query, query_keywords)
            if query_topic == msg.get("topic"):
                score += 5
            
            # Score based on recency (newer is better)
            msg_index = msg["id"]
            recency_score = msg_index / len(self.messages)  # 0 to 1
            score += recency_score * 2
            
            relevance_scores[msg_index] = score
        
        # Get top relevant messages
        top_indices = sorted(relevance_scores.keys(), 
                            key=lambda idx: relevance_scores[idx],
                            reverse=True)[:max_messages]
        
        # Sort by original order
        top_indices.sort()
        
        # Get messages
        relevant_messages = [self.messages[idx] for idx in top_indices]
        
        # Convert to simple format
        return [{"role": m["role"], "content": m["content"]} for m in relevant_messages]
    
    def update_importance_scores(self):
        """Update importance scores for all messages based on current context."""
        # Recalculate importance for all messages
        for msg in self.messages:
            msg_id = msg["id"]
            role = msg["role"]
            importance = self._calculate_importance(msg, role)
            self.message_importance[msg_id] = importance
    
    def _calculate_importance(self, message: Dict[str, Any], role: str) -> float:
        """
        Calculate importance score for a message.
        
        Args:
            message: Message dictionary
            role: Message role
            
        Returns:
            Importance score (higher is more important)
        """
        score = 0
        
        # System messages are most important
        if role == "system":
            return 100
        
        # Recent messages are important
        recency = message["id"] / max(1, len(self.messages))
        score += recency * 20  # 0-20 points for recency
        
        # Messages with code are important
        if "code_snippets" in message:
            score += 15
        
        # Messages on current topic are important
        if message.get("topic") == self.current_topic:
            score += 10
        
        # Messages with many entities are important
        entity_count = len(message.get("entities", []))
        score += min(entity_count * 2, 10)  # Up to 10 points for entities
        
        # Messages with questions are important
        if "?" in message["content"]:
            score += 5
        
        # User messages slightly more important than assistant
        if role == "user":
            score += 3
        
        return score
    
    def _optimize_context_if_needed(self):
        """Check if context optimization is needed and perform if necessary."""
        # Check if we've exceeded max messages
        if len(self.messages) > self.max_messages:
            self._optimize_context()
            return
        
        # Check if we've exceeded max context length
        total_tokens = sum(m.get("tokens", 0) for m in self.messages)
        if total_tokens > self.max_context_length:
            self._optimize_context()
            return
        
        # Check if it's been a while since last optimization
        now = datetime.datetime.now()
        time_since_optimization = (now - self.last_optimization).total_seconds()
        if time_since_optimization > 300:  # 5 minutes
            self.update_importance_scores()
            self.last_optimization = now
    
    def _optimize_context(self):
        """Optimize conversation context by removing less important messages."""
        # Update importance scores
        self.update_importance_scores()
        
        # Always keep system messages
        system_messages = [m for m in self.messages if m["role"] == "system"]
        
        # Always keep the most recent messages (last 2 turns)
        recent_count = min(4, len(self.messages))
        recent_messages = self.messages[-recent_count:]
        
        # Get remaining messages
        middle_messages = [m for m in self.messages 
                          if m["role"] != "system" and m not in recent_messages]
        
        # Sort by importance
        middle_messages.sort(key=lambda m: self.message_importance.get(m["id"], 0), reverse=True)
        
        # Keep most important messages within token budget
        kept_messages = system_messages + recent_messages
        kept_tokens = sum(m.get("tokens", 0) for m in kept_messages)
        
        # Calculate how many more tokens we can include
        remaining_tokens = self.max_context_length - kept_tokens
        
        # Add important messages until we reach the limit
        for msg in middle_messages:
            msg_tokens = msg.get("tokens", 0)
            if kept_tokens + msg_tokens <= self.max_context_length:
                kept_messages.append(msg)
                kept_tokens += msg_tokens
            
            if len(kept_messages) >= self.max_messages:
                break
        
        # Sort by original order
        kept_messages.sort(key=lambda m: m["id"])
        
        # Update messages list
        self.messages = kept_messages
        
        # Update last optimization timestamp
        self.last_optimization = datetime.datetime.now()
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        
        This is a simple approximation. In production, you might want to use
        a tokenizer from the LLM provider.
        """
        # Simple approximation: ~4 chars per token for English text
        return len(text) // 4 + 1
    
    def _extract_entities_and_keywords(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract entities and keywords from text.
        
        Returns:
            Tuple of (entities, keywords)
        """
        # This is a simplified implementation
        # In production, consider using NLP libraries like spaCy
        
        # Extract potential code-related terms
        code_keywords = set()
        code_patterns = [
            r'def\s+(\w+)',  # Function names
            r'class\s+(\w+)',  # Class names
            r'import\s+(\w+)',  # Import names
            r'from\s+(\w+)',  # From import
            r'(\w+)\s*=',  # Variable assignments
            r'(\w+)\(',  # Function calls
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            code_keywords.update(matches)
        
        # Extract general keywords (simplified)
        words = re.findall(r'\b\w{4,}\b', text.lower())
        general_keywords = [w for w in words if w not in ['this', 'that', 'with', 'from', 'have', 'what']]
        
        # Combine and limit
        all_keywords = list(code_keywords) + general_keywords
        keywords = list(set(all_keywords))[:20]  # Limit to 20 unique keywords
        
        # Extract potential entities (simplified)
        # In production, use NER from spaCy or similar
        entity_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Proper names
            r'([A-Z][A-Z0-9_]+)',  # ALL_CAPS constants
            r'"([^"]+)"',  # Quoted strings
            r"'([^']+)'",  # Single-quoted strings
        ]
        
        entities = []
        for pattern in entity_patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        entities = list(set(entities))[:10]  # Limit to 10 unique entities
        
        return entities, keywords
    
    def _extract_code(self, text: str) -> List[str]:
        """Extract code snippets from text."""
        # Look for markdown code blocks
        code_blocks = re.findall(r'```(?:python)?(.*?)```', text, re.DOTALL)
        
        # If no markdown blocks, look for indented code
        if not code_blocks:
            lines = text.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                if re.match(r'^\s{4}', line) or line.startswith('\t'):
                    in_code_block = True
                    code_lines.append(line.strip())
                elif in_code_block and line.strip() == '':
                    code_lines.append('')
                elif in_code_block:
                    in_code_block = False
                    if code_lines:
                        code_blocks.append('\n'.join(code_lines))
                        code_lines = []
            
            if code_lines:
                code_blocks.append('\n'.join(code_lines))
        
        return [block.strip() for block in code_blocks if block.strip()]
    
    def _detect_topic(self, text: str, keywords: List[str]) -> str:
        """
        Detect the topic of a message.
        
        Args:
            text: Message text
            keywords: Extracted keywords
            
        Returns:
            Detected topic
        """
        # Define topic keywords
        topic_keywords = {
            "code_help": ["help", "error", "bug", "fix", "problem", "issue", "debug"],
            "explanation": ["explain", "understand", "mean", "concept", "how", "why"],
            "code_generation": ["create", "generate", "write", "implement", "code", "function", "class"],
            "data_analysis": ["data", "analyze", "plot", "graph", "pandas", "dataframe"],
            "web_dev": ["web", "html", "css", "javascript", "flask", "django"],
            "machine_learning": ["model", "train", "predict", "ml", "ai", "neural", "learn"],
            "database": ["database", "sql", "query", "table", "join", "select"],
            "file_io": ["file", "read", "write", "open", "save", "load"],
        }
        
        # Score each topic
        topic_scores = {}
        for topic, topic_kw in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in topic_kw)
            
            # Check for direct mentions in text
            for kw in topic_kw:
                if kw in text.lower():
                    score += 0.5
            
            topic_scores[topic] = score
        
        # Get highest scoring topic
        if topic_scores:
            best_topic = max(topic_scores.items(), key=lambda x: x[1])
            if best_topic[1] > 0:
                return best_topic[0]
        
        # Default topic
        return "general"
