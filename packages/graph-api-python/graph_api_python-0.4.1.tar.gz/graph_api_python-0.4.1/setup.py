"""
Graph Elements - A Python library for graph-based data structures and queries

This library provides TypeScript-equivalent functionality for managing graph elements
with a powerful fluent query API.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="graph-api-python",
    version="1.0.0",
    author="damylen",
    author_email="damylen@users.noreply.github.com",
    description="A Python library for graph-based data structures and queries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/damylen/graph-api-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Database",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/damylen/graph-api-python/issues",
        "Source": "https://github.com/damylen/graph-api-python",
    },
)
