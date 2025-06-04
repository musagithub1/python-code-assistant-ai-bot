"""
API Integration Module

This module handles interactions with language model APIs.
"""

from openai import OpenAI
import os
from typing import List, Dict, Any

class APIClient:
    """Handles interactions with language model APIs."""
    
    def __init__(self, config_manager):
        """Initialize API client with configuration manager."""
        self.config_manager = config_manager
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the API client based on configuration."""
        provider = self.config_manager.get("api", "provider", "openrouter")
        base_url = self.config_manager.get("api", "base_url", "https://openrouter.ai/api/v1")
        api_key = self.config_manager.get_api_key()
        
        if not api_key:
            raise ValueError("API key not found. Please set the appropriate environment variable.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def get_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Get completion from the language model API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            
        Returns:
            Generated text response
        """
        if not self.client:
            self._initialize_client()
            
        model = self.config_manager.get("api", "model", "tngtech/deepseek-r1t-chimera:free")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: Failed to get completion from API. {str(e)}"
    
    def get_streaming_completion(self, messages: List[Dict[str, str]], callback, temperature: float = 0.7):
        """
        Get streaming completion from the language model API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            callback: Function to call with each chunk of the response
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        """
        if not self.client:
            self._initialize_client()
            
        model = self.config_manager.get("api", "model", "tngtech/deepseek-r1t-chimera:free")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    callback(chunk.choices[0].delta.content)
        except Exception as e:
            callback(f"\nError: Failed to get streaming completion from API. {str(e)}")
