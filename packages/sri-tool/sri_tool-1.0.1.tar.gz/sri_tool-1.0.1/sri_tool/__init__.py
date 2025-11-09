"""
SRI Tool - Subresource Integrity Management CLI Tool

A tool for generating, verifying, and managing
Subresource Integrity (SRI) hashes in HTML files.
"""

__version__ = "1.0.1"
__author__ = "adasThePro"
__license__ = "MIT"

from .generator import SRIGenerator
from .validator import SRIValidator

__all__ = ["SRIGenerator", "SRIValidator"]
