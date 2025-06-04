"""
Configuration Management Module

This module handles configuration settings for the chatbot with secure storage options.
"""

import os
import configparser
from typing import Dict, Any

class ConfigManager:
    """Manages configuration settings for the chatbot with secure storage options."""
    
    DEFAULT_CONFIG = {
        "api": {
            "provider": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "tngtech/deepseek-r1t-chimera:free",
            "api_key_env_var": "OPENROUTER_API_KEY"
        },
        "app": {
            "save_folder": "bot_outputs",
            "max_conversation_turns": 10,
            "code_execution_timeout": 5,
            "auto_save_code": True,
            "syntax_highlighting": True
        },
        "ui": {
            "use_rich_ui": True,
            "bot_name": "Advanced Python Assistant",
            "primary_color": "cyan",
            "secondary_color": "green",
            "error_color": "red",
            "success_color": "magenta"
        }
    }
    
    def __init__(self, config_file: str = "config.ini"):
        """Initialize configuration manager with specified config file."""
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists."""
        if os.path.exists(self.config_file):
            try:
                config = configparser.ConfigParser()
                config.read(self.config_file)
                return {section: dict(config[section]) for section in config.sections()}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        config = configparser.ConfigParser()
        
        for section, options in self.DEFAULT_CONFIG.items():
            config[section] = {}
            for key, value in options.items():
                # Ensure all config values are ASCII-compatible for Windows
                if isinstance(value, str):
                    # Replace or remove non-ASCII characters
                    value = value.encode('ascii', 'replace').decode('ascii')
                config[section][key] = str(value)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
        except UnicodeEncodeError:
            # Fallback to ASCII encoding if UTF-8 fails
            with open(self.config_file, 'w', encoding='ascii', errors='replace') as f:
                config.write(f)
        
        return self.DEFAULT_CONFIG
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to default."""
        try:
            return self.config.get(section, {}).get(key, default)
        except:
            return default
    
    def get_api_key(self) -> str:
        """Securely retrieve API key from environment variable."""
        env_var = self.get("api", "api_key_env_var", "OPENROUTER_API_KEY")
        api_key = os.environ.get(env_var)
        
        if not api_key:
            # Fallback to direct config value if needed
            api_key = self.get("api", "api_key", "")
            
        return api_key
    
    def save(self) -> None:
        """Save current configuration to file."""
        config = configparser.ConfigParser()
        
        for section, options in self.config.items():
            config[section] = {}
            for key, value in options.items():
                # Ensure all config values are ASCII-compatible for Windows
                if isinstance(value, str):
                    # Replace or remove non-ASCII characters
                    value = value.encode('ascii', 'replace').decode('ascii')
                config[section][key] = str(value)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
        except UnicodeEncodeError:
            # Fallback to ASCII encoding if UTF-8 fails
            with open(self.config_file, 'w', encoding='ascii', errors='replace') as f:
                config.write(f)
