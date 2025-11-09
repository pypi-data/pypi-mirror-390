from setuptools import setup, find_packages

setup(
    name="agtest",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
    "google-generativeai>=0.8.5",
    "openai>=1.55.0,<2.0.0",
    "anthropic>=0.33.0,<0.35.0"
    ],
    entry_points={
        "console_scripts": [
            "agent-cli = agent.agent_ai:agent_ai"
        ]
    }
)
