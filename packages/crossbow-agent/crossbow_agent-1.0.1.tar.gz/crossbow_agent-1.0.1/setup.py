#!/usr/bin/env python3
"""
CrossBow Security Agent - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="crossbow-agent",
    version="1.0.1",
    author="Harish Santhanalakshmi Ganesan",
    author_email="harishsg99@gmail.com",
    description="World's first fully autonomous AI security engineer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harishsg99/crossbow-agent",
    project_urls={
        "Bug Tracker": "https://github.com/harishsg99/crossbow-agent/issues",
        "Documentation": "https://github.com/harishsg99/crossbow-agent",
        "Source Code": "https://github.com/harishsg99/crossbow-agent",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.9",
    install_requires=[
        "agno>=2.2.6",
        "anthropic>=0.72.0",
        "openai>=2.6.1",
        "google-genai>=1.47.0",
        "google-generativeai>=0.8.5",
        "python-dotenv>=1.2.1",
        "duckduckgo-search>=8.1.1",
        "ddgs>=9.7.0",
        "mcp>=1.21.0",
        "paramiko>=4.0.0",
        "sqlalchemy>=2.0.44",
        "requests>=2.32.5",
        "rich>=14.2.0",
        "dnspython>=2.8.0",
        "bandit>=1.8.6",
        "textual>=0.90.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
        ],
        "full": [
            "semgrep>=1.85.0",
            "litellm>=1.79.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "crossbow=crossbow_cli:main",
            "crossbow-tui=crossbow_tui:main",
        ],
    },
    include_package_data=True,
    keywords=[
        "security",
        "testing",
        "penetration-testing",
        "security-testing",
        "ai",
        "agents",
        "llm",
        "cybersecurity",
        "vulnerability-assessment",
        "threat-intelligence",
        "soc",
        "red-team",
        "blue-team",
        "dfir",
        "forensics",
    ],
    zip_safe=False,
)
