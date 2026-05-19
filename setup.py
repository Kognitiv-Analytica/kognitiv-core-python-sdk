"""
Kognitiv Core Python SDK - Setup Configuration

This file enables installation via:
    pip install -e .
    python setup.py install
    pip install -e ".[dev]"  # with dev dependencies
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kognitiv",
    version="2.7.1",
    author="Kognitiv Team",
    author_email="support@kognitiv.ai",
    description="Python SDK for Kognitiv Core API - AI for Educational Institutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aristotekujialphonse/kognitiv-core-sdk",
    project_urls={
        "Documentation": "https://www.kognitivcore.app",
        "API Reference": "https://www.kognitivcore.app",
        "Source Code": "https://github.com/aristotekujialphonse/kognitiv-core-sdk",
        "Issue Tracker": "https://github.com/aristotekujialphonse/kognitiv-core-sdk/issues",
        "Changelog": "https://github.com/aristotekujialphonse/kognitiv-core-sdk/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",  # Async HTTP client
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "sphinx>=5.0",  # Documentation
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai kognitiv education api sdk learning lms canvas blackboard moodle",
    license="Proprietary (Educational)",
)
