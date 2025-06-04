"""
Integration test script for the Python Bot Upgraded.

This script performs end-to-end validation of the integrated application.
"""

import os
import sys
import unittest
import requests
import time
import subprocess
import signal
import json
from multiprocessing import Process

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class IntegrationTest(unittest.TestCase):
    """Integration tests for the Python Bot Upgraded."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment by starting the web server."""
        # Start the web server in a separate process
        cls.server_process = subprocess.Popen(
            ["python", "main.py", "--web", "--port", "5001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Base URL for API requests
        cls.base_url = "http://localhost:5001"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment by stopping the web server."""
        # Stop the web server
        cls.server_process.terminate()
        cls.server_process.wait()
    
    def test_chat_endpoint(self):
        """Test the chat API endpoint."""
        # Send a chat message
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"message": "How do I read a CSV file in pandas?"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(data["response"])  # Response should not be empty
        
        # Check if response contains pandas information
        self.assertTrue(
            "pandas" in data["response"].lower() or 
            "csv" in data["response"].lower() or
            "read_csv" in data["response"].lower()
        )
    
    def test_code_execution_endpoint(self):
        """Test the code execution API endpoint."""
        # Send code to execute
        code = "x = 5\ny = 10\nprint(x + y)"
        response = requests.post(
            f"{self.base_url}/api/execute",
            json={"code": code}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("output", data)
        self.assertIn("success", data)
        self.assertTrue(data["success"])
        self.assertEqual(data["output"].strip(), "15")
    
    def test_history_endpoint(self):
        """Test the history API endpoint."""
        # First send a chat message
        requests.post(
            f"{self.base_url}/api/chat",
            json={"message": "What is Python?"}
        )
        
        # Get history
        response = requests.get(f"{self.base_url}/api/history")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("messages", data)
        self.assertTrue(len(data["messages"]) > 0)
    
    def test_clear_endpoint(self):
        """Test the clear API endpoint."""
        # First send a chat message
        requests.post(
            f"{self.base_url}/api/chat",
            json={"message": "Hello"}
        )
        
        # Clear history
        response = requests.post(f"{self.base_url}/api/clear")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)
        self.assertTrue(data["success"])
        
        # Check if history is cleared
        history_response = requests.get(f"{self.base_url}/api/history")
        history_data = history_response.json()
        self.assertEqual(len(history_data["messages"]), 0)
    
    def test_categorize_endpoint(self):
        """Test the code categorization API endpoint."""
        # Send code to categorize
        code = """
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df.describe()
plt.plot(df['x'], df['y'])
plt.show()
"""
        response = requests.post(
            f"{self.base_url}/api/categorize",
            json={"code": code}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("suggestions", data)
        self.assertTrue(len(data["suggestions"]) > 0)
        
        # First suggestion should be data_analysis
        self.assertEqual(data["suggestions"][0]["category"], "data_analysis")

if __name__ == '__main__':
    unittest.main()
