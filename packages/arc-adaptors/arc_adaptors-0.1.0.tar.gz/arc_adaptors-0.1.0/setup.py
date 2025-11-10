#!/usr/bin/env python3
"""
ARC Adaptors - Integration adaptors for the Agent Remote Communication Protocol
"""

from setuptools import setup, find_packages

setup(
    name="arc-adaptors",
    version="0.1.0",
    description="Adaptors for the Agent Remote Communication (ARC) Protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ARC Protocol Team",
    author_email="moein.roghani@proton.me",
    url="https://github.com/arcprotocol/arc-adaptors",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "arc-sdk>=1.2.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "mistralai>=0.0.7",
        "langchain>=0.0.267",
        "llama-index>=0.8.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "mistral": ["mistralai>=0.0.7"],
        "langchain": ["langchain>=0.0.267"],
        "llama-index": ["llama-index>=0.8.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)