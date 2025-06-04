import unittest
import os
import tempfile
from config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ini')
        self.temp_file.close()
        self.config_file = self.temp_file.name
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary file
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
    
    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        config_manager = ConfigManager(self.config_file)
        
        # Check if default config was created
        self.assertTrue(os.path.exists(self.config_file))
        
        # Check if default values are set correctly
        self.assertEqual(
            config_manager.get("api", "provider"),
            "openrouter"
        )
        self.assertEqual(
            config_manager.get("app", "max_conversation_turns"),
            10
        )
        self.assertEqual(
            config_manager.get("ui", "bot_name"),
            "Advanced Python Assistant"
        )
    
    def test_get_with_fallback(self):
        """Test get method with fallback to default value."""
        config_manager = ConfigManager(self.config_file)
        
        # Test existing value
        self.assertEqual(
            config_manager.get("api", "provider"),
            "openrouter"
        )
        
        # Test non-existing value with default
        self.assertEqual(
            config_manager.get("api", "non_existing", "default_value"),
            "default_value"
        )
        
        # Test non-existing section with default
        self.assertEqual(
            config_manager.get("non_existing", "key", "default_value"),
            "default_value"
        )
    
    def test_get_api_key(self):
        """Test get_api_key method."""
        config_manager = ConfigManager(self.config_file)
        
        # Test with environment variable
        os.environ["OPENROUTER_API_KEY"] = "test_api_key"
        self.assertEqual(config_manager.get_api_key(), "test_api_key")
        
        # Clean up
        del os.environ["OPENROUTER_API_KEY"]
    
    def test_save(self):
        """Test save method."""
        config_manager = ConfigManager(self.config_file)
        
        # Modify config
        config_manager.config["api"]["provider"] = "modified_provider"
        config_manager.config["ui"]["bot_name"] = "Modified Bot Name"
        
        # Save config
        config_manager.save()
        
        # Create new instance to load from file
        new_config_manager = ConfigManager(self.config_file)
        
        # Check if values were saved correctly
        self.assertEqual(
            new_config_manager.get("api", "provider"),
            "modified_provider"
        )
        self.assertEqual(
            new_config_manager.get("ui", "bot_name"),
            "Modified Bot Name"
        )

if __name__ == '__main__':
    unittest.main()
