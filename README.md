Python Code Assistant AI Bot

This project is an advanced Python Code Assistant Bot featuring a modular architecture, intelligent context management, integrated code execution, and user interfaces for both terminal (Rich) and web (Flask). Designed as an AI-powered tool to enhance developer productivity.

Key Features

•
Modular Design: Easily maintainable and extensible codebase.

•
Advanced Context Management: Utilizes topic detection and relevance scoring for coherent conversations.

•
Code Execution: Integrated environment for running Python code snippets safely.

•
Configurable API: Supports different LLM API providers (e.g., OpenRouter, OpenAI) via config.ini.

•
Dual Interfaces:

•
Terminal UI: Rich-text based interface for command-line usage.

•
Web UI: Modern Flask-based web interface with syntax highlighting.



•
Comprehensive Testing: Includes unit and integration tests for reliability.

Setup (Windows)

1.
Clone/Download: Ensure you have the project files in a local folder (e.g., C:\Users\rajam\Downloads\python_bot_upgraded).

2.
Create config.ini: Copy config.ini.template to config.ini and add your API key.

3.
Open Command Prompt/PowerShell: Navigate to the project directory:

4.
Create Virtual Environment:

5.
Activate Virtual Environment:

6.
Install Dependencies:

Usage

Make sure your virtual environment is active.

•
Terminal UI:

•
Web UI:

Testing

Ensure pytest is installed (pip install pytest) and run from the project root directory:

Plain Text


pytest


Project Structure

Plain Text


python_bot_upgraded/
├── .git/              # Git repository data (hidden)
├── api/               # API client logic
├── code_execution/    # Code execution module
├── config/            # Configuration management
├── conversation/      # Conversation and context handling
├── tests/             # Unit and integration tests
├── ui/                # User interface modules
│   ├── terminal/
│   └── web/
├── utils/             # Utility functions
├── .gitignore         # Files ignored by Git
├── config.ini.template # Configuration template
├── config.ini         # Local configuration (ignored by Git)
├── main.py            # Main application logic
├── requirements.txt   # Project dependencies
├── README.md          # This file
├── run.py             # Entry point script
├── setup.py           # Packaging setup
└── validation_report.md # Validation results


Note: Remember to keep your config.ini file (with your API key) out of version control. The .gitignore file is configured to help with this.

