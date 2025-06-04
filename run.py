import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from main.py
from main import main

# Run the application
if __name__ == "__main__":
    main()
