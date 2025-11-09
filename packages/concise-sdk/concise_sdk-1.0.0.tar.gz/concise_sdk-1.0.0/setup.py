"""
Setup script for Concise Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="concise-sdk",
    version="1.0.0",
    author="Concise Team",
    author_email="support@concise.dev",
    description="Official Python SDK for Concise - Token compression for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/concise/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="llm, compression, openai, tokens, ai, nlp",
    project_urls={
        "Documentation": "https://docs.concise.dev",
        "Source": "https://github.com/concise/python-sdk",
        "Bug Reports": "https://github.com/concise/python-sdk/issues",
    },
)
