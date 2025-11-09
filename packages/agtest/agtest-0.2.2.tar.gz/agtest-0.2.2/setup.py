from setuptools import setup, find_packages

setup(
    name="agtest",
    version="0.2.2",
    packages=find_packages(),
    install_requires=[
    "google-generativeai>=0.8.5",
    "openai>=1.55.1",
    "anthropic>=0.34.1"
    ],
    entry_points={
        "console_scripts": [
            "agent-cli = agent.agent_ai:agent_ai"
        ]
    }
)
