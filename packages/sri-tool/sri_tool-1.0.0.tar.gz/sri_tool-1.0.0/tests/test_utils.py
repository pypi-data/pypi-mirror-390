"""Tests for SRI Tool utilities."""

import hashlib
import base64
import pytest

from sri_tool.utils import (
    calculate_sri_hash,
    calculate_multiple_hashes,
    is_remote_url,
    is_data_uri,
    format_size,
    should_add_crossorigin
)


class TestCalculateSRIHash:
    """Tests for calculate_sri_hash function."""
    
    def test_sha256(self):
        """Test SHA-256 hash calculation."""
        content = b"Hello, World!"
        expected_hash = hashlib.sha256(content).digest()
        expected_b64 = base64.b64encode(expected_hash).decode('utf-8')
        
        result = calculate_sri_hash(content, 'sha256')
        assert result == f"sha256-{expected_b64}"
    
    def test_sha384(self):
        """Test SHA-384 hash calculation (default)."""
        content = b"Test content"
        expected_hash = hashlib.sha384(content).digest()
        expected_b64 = base64.b64encode(expected_hash).decode('utf-8')
        
        result = calculate_sri_hash(content, 'sha384')
        assert result == f"sha384-{expected_b64}"
    
    def test_sha512(self):
        """Test SHA-512 hash calculation."""
        content = b"Another test"
        expected_hash = hashlib.sha512(content).digest()
        expected_b64 = base64.b64encode(expected_hash).decode('utf-8')
        
        result = calculate_sri_hash(content, 'sha512')
        assert result == f"sha512-{expected_b64}"
    
    def test_invalid_algorithm(self):
        """Test that invalid algorithm raises ValueError."""
        with pytest.raises(ValueError):
            calculate_sri_hash(b"test", 'md5')
    
    def test_empty_content(self):
        """Test hash calculation with empty content."""
        content = b""
        result = calculate_sri_hash(content, 'sha384')
        assert result.startswith('sha384-')
        assert len(result) > 7


class TestCalculateMultipleHashes:
    """Tests for calculate_multiple_hashes function."""
    
    def test_multiple_algorithms(self):
        """Test calculating multiple hashes."""
        content = b"Test"
        algorithms = ['sha256', 'sha384', 'sha512']
        
        results = calculate_multiple_hashes(content, algorithms)
        
        assert len(results) == 3
        assert results[0].startswith('sha256-')
        assert results[1].startswith('sha384-')
        assert results[2].startswith('sha512-')
    
    def test_single_algorithm(self):
        """Test with single algorithm in list."""
        content = b"Test"
        algorithms = ['sha384']
        
        results = calculate_multiple_hashes(content, algorithms)
        
        assert len(results) == 1
        assert results[0].startswith('sha384-')


class TestIsRemoteUrl:
    """Tests for is_remote_url function."""
    
    def test_http_url(self):
        """Test HTTP URL detection."""
        assert is_remote_url('http://example.com/file.js') is True
    
    def test_https_url(self):
        """Test HTTPS URL detection."""
        assert is_remote_url('https://cdn.example.com/style.css') is True
    
    def test_relative_path(self):
        """Test relative path is not detected as URL."""
        assert is_remote_url('./file.js') is False
        assert is_remote_url('../style.css') is False
    
    def test_absolute_path(self):
        """Test absolute path is not detected as URL."""
        assert is_remote_url('/var/www/file.js') is False
    
    def test_data_uri(self):
        """Test data URI is not detected as remote URL."""
        assert is_remote_url('data:text/javascript;base64,abc123') is False


class TestIsDataUri:
    """Tests for is_data_uri function."""
    
    def test_data_uri(self):
        """Test data URI detection."""
        assert is_data_uri('data:text/javascript;base64,abc123') is True
        assert is_data_uri('data:image/png;base64,iVBORw0KG') is True
    
    def test_regular_url(self):
        """Test regular URL is not detected as data URI."""
        assert is_data_uri('http://example.com/file.js') is False
        assert is_data_uri('https://example.com/file.js') is False
    
    def test_relative_path(self):
        """Test relative path is not detected as data URI."""
        assert is_data_uri('./file.js') is False


class TestFormatSize:
    """Tests for format_size function."""
    
    def test_bytes(self):
        """Test formatting bytes."""
        assert format_size(100) == "100.00 B"
        assert format_size(1000) == "1000.00 B"
    
    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(2048) == "2.00 KB"
    
    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(5 * 1024 * 1024) == "5.00 MB"
    
    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.00 GB"


class TestShouldAddCrossorigin:
    """Tests for should_add_crossorigin function."""
    
    def test_remote_url(self):
        """Test crossorigin should be added for remote URLs."""
        assert should_add_crossorigin('https://cdn.example.com/file.js') is True
        assert should_add_crossorigin('http://example.com/file.css') is True
    
    def test_local_path(self):
        """Test crossorigin should not be added for local paths."""
        assert should_add_crossorigin('./file.js') is False
        assert should_add_crossorigin('/var/www/file.css') is False
