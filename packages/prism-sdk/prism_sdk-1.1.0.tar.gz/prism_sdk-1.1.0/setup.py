from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prism-sdk",
    version="1.1.0",
    author="Prism Labs",
    author_email="support@prismmeta.com",
    description="Official Python SDK for Prism Meta - AI-Powered Trust Verification API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prismmeta/prism-sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/prismmeta/prism-sdk-python/issues",
        "Documentation": "https://docs.prismmeta.ai/sdk/python",
        "API Reference": "https://api.prismmeta.ai/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.0.0",
            "mkdocstrings[python]>=0.19.0",
        ],
    },
    keywords="prism, trust, verification, fact-checking, ai, api, sdk",
)