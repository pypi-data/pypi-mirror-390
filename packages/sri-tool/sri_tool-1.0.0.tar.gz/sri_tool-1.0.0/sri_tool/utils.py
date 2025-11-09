"""Utility functions for SRI operations."""

import hashlib
import base64
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Optional, List
import logging


def calculate_sri_hash(content: bytes, algorithm: str = 'sha384') -> str:
    """
    Calculate SRI hash for given content.
    
    Args:
        content: File content as bytes
        algorithm: Hash algorithm (sha256, sha384, sha512)
        
    Returns:
        SRI hash string in format: 'algorithm-base64hash'
        
    Raises:
        ValueError: If algorithm is not supported
    """
    algorithm = algorithm.lower()
    
    if algorithm == 'sha256':
        hash_obj = hashlib.sha256(content)
    elif algorithm == 'sha384':
        hash_obj = hashlib.sha384(content)
    elif algorithm == 'sha512':
        hash_obj = hashlib.sha512(content)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Use sha256, sha384, or sha512.")
    
    hash_base64 = base64.b64encode(hash_obj.digest()).decode('utf-8')
    return f"{algorithm}-{hash_base64}"


def calculate_multiple_hashes(content: bytes, algorithms: List[str]) -> List[str]:
    """
    Calculate multiple SRI hashes for the same content.
    
    Args:
        content: File content as bytes
        algorithms: List of hash algorithms
        
    Returns:
        List of SRI hash strings
    """
    return [calculate_sri_hash(content, algo) for algo in algorithms]


def fetch_remote_content(url: str, timeout: int = 10, logger: Optional[logging.Logger] = None) -> Optional[bytes]:
    """
    Fetch content from a remote URL using urllib.
    
    Args:
        url: Remote URL to fetch
        timeout: Request timeout in seconds
        logger: Optional logger instance
        
    Returns:
        Content as bytes or None if fetch fails
    """
    try:
        req = Request(url, headers={
            'User-Agent': 'sri-tool/1.0.0'
        })
        
        with urlopen(req, timeout=timeout) as response:
            return response.read()
            
    except HTTPError as e:
        if logger:
            logger.error(f"Failed to fetch {url}: HTTP {e.code} {e.reason}")
        return None
    except URLError as e:
        if logger:
            logger.error(f"Failed to fetch {url}: {e.reason}")
        return None
    except Exception as e:
        if logger:
            logger.error(f"Failed to fetch {url}: {e}")
        return None


def is_remote_url(path: str) -> bool:
    """Check if a path is a remote URL."""
    parsed = urlparse(path)
    return parsed.scheme in ('http', 'https')


def resolve_asset_path(html_file_path: Path, asset_path: str) -> Optional[Path]:
    """
    Resolve asset path to absolute file system path.
    
    Args:
        html_file_path: Path to the HTML file
        asset_path: Asset path from HTML (relative or absolute)
        
    Returns:
        Resolved Path object or None if not found
    """
    asset_path = asset_path.split('?')[0].split('#')[0]
    
    if is_remote_url(asset_path):
        return None
    
    if Path(asset_path).is_absolute():
        path = Path(asset_path)
        if path.exists():
            return path
        return None
    
    html_dir = html_file_path.parent
    
    asset_full_path = (html_dir / asset_path).resolve()
    if asset_full_path.exists():
        return asset_full_path
    
    for parent in [html_dir] + list(html_dir.parents):
        potential_path = (parent / asset_path.lstrip('/')).resolve()
        if potential_path.exists():
            return potential_path
    
    return None


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def is_data_uri(uri: str) -> bool:
    """Check if a URI is a data URI."""
    return uri.startswith('data:')


def should_add_crossorigin(url: str) -> bool:
    """Determine if crossorigin attribute should be added."""
    return is_remote_url(url)
