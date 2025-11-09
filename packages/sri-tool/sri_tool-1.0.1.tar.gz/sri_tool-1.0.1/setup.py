"""Setup configuration for SRI Tool."""

from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="sri-tool",
    version="1.0.1",
    author="adasThePro",
    description="A CLI tool for managing Subresource Integrity (SRI) hashes in HTML files - no external dependencies!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adasThePro/sri-tool",
    packages=find_packages(),
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15"
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sri-tool=sri_tool.cli:main",
            "sri=sri_tool.cli:main",
        ],
    },
    keywords=["python", "sri", "subresource-integrity", "web-security", "cli", "html", "css", "javascript", "hash", "validator", "generator", "integrity", "assets"],
    project_urls={
        "Homepage": "https://github.com/adasThePro/sri-tool",
        "Repository": "https://github.com/adasThePro/sri-tool",
        "Issues": "https://github.com/adasThePro/sri-tool/issues"
    },
)
