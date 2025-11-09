Agtest-AI: Automated Test Generation Agent

Agtest-AI is an intelligent command-line tool and Python library that automatically generates unit tests for FastAPI-based applications.
It analyzes source code (controllers and services), understands dependencies and logic, and produces complete, production-ready pytest files that align with your project’s testing standards.

Purpose

To automate the generation of realistic and maintainable FastAPI unit tests.
Agtest-AI eliminates repetitive manual effort and ensures consistent, rule-compliant testing across projects.

Key Features

Automatic File Type Detection — Identifies whether the input file is a controller or service.
AI-Powered Test Generation — Uses Google Gemini API to analyze source code and generate test cases.
Project-Standard Compliance — Follows internal test structures, including:
-Mocked DB sessions (MagicMock(spec=Session))
-Configured TestClient with middleware and dependency overrides
-Exception handling for both sync and async endpoints
-Separate success and failure test cases per route
-Configurable Output — Control the output directory and generation parameters.
-Role-Aware Prompts — Creates distinct instructions for controllers and services to ensure context-aware test generation.

Configuration

Agtest-AI supports environment-based configuration for flexible setup:-MODEL_NAME,MAX_TOKENS,TEMPERATURE,API_KEY
The output directory can be modified directly in the runner configuration.

Installation
pip install agtest

Usage
Run the agent directly from the command line:
agent-cli

You’ll be prompted to provide:
File path for test generation
Gemini API key
Output directory 
Router file path (for controllers)

The generated tests will be saved as:tests_<filename>.py

Why Agtest-AI:
Save hours of manual testing effort.
Maintain consistent and accurate unit tests.
Improve test coverage automatically.

It supports google gemini api key and paid vertion of OpenAI api key.
It gives line and file coverage of above 85%.
License
Distributed under the MIT License. See LICENSE for details.
