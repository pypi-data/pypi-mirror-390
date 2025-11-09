"""Tests for SRI Validator."""

import tempfile
from pathlib import Path

from sri_tool.validator import SRIValidator
from sri_tool.utils import calculate_sri_hash


class TestSRIValidator:
    """Tests for SRIValidator class."""
    
    def test_initialization(self):
        """Test validator initialization."""
        validator = SRIValidator()
        assert validator.verbose is False
        assert validator.results == []
    
    def test_extract_sri_info(self):
        """Test extracting SRI information from HTML."""
        validator = SRIValidator()
        
        html = '''
        <link rel="stylesheet" href="style.css" integrity="sha384-abc123">
        <script src="script.js" integrity="sha384-def456"></script>
        '''
        
        assets = validator.extract_sri_info(html)
        
        assert len(assets) == 2
        assert assets[0]['type'] == 'stylesheet'
        assert assets[0]['url'] == 'style.css'
        assert assets[0]['integrity'] == 'sha384-abc123'
        assert assets[1]['type'] == 'script'
        assert assets[1]['url'] == 'script.js'
        assert assets[1]['integrity'] == 'sha384-def456'
    
    def test_extract_sri_info_no_integrity(self):
        """Test extracting when no integrity attributes present."""
        validator = SRIValidator()
        
        html = '''
        <link rel="stylesheet" href="style.css">
        <script src="script.js"></script>
        '''
        
        assets = validator.extract_sri_info(html)
        assert len(assets) == 0
    
    def test_validate_integrity_valid(self):
        """Test validating correct integrity hash."""
        validator = SRIValidator()
        
        content = b"test content"
        expected_hash = calculate_sri_hash(content, 'sha384')
        
        is_valid, actual = validator.validate_integrity(content, expected_hash)
        
        assert is_valid is True
        assert actual == expected_hash
    
    def test_validate_integrity_invalid(self):
        """Test validating incorrect integrity hash."""
        validator = SRIValidator()
        
        content = b"test content"
        wrong_hash = "sha384-wronghashvalue"
        
        is_valid, actual = validator.validate_integrity(content, wrong_hash)
        
        assert is_valid is False
        assert actual is not None
        assert actual != wrong_hash
    
    def test_validate_html_file_valid(self):
        """Test validating HTML file with valid SRI hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_content = b"body { margin: 0; }"
            css_file = tmppath / "style.css"
            css_file.write_bytes(css_content)
            
            correct_hash = calculate_sri_hash(css_content, 'sha384')
            
            html_file = tmppath / "index.html"
            html_content = f'<link rel="stylesheet" href="style.css" integrity="{correct_hash}">'
            html_file.write_text(html_content)
            
            validator = SRIValidator()
            result = validator.validate_html_file(html_file)
            
            assert result['valid'] == 1
            assert result['invalid'] == 0
            assert result['assets'][0]['status'] == 'valid'
    
    def test_validate_html_file_invalid(self):
        """Test validating HTML file with invalid SRI hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_content = b"body { margin: 0; }"
            css_file = tmppath / "style.css"
            css_file.write_bytes(css_content)
            
            wrong_hash = "sha384-wronghashvalue"
            
            html_file = tmppath / "index.html"
            html_content = f'<link rel="stylesheet" href="style.css" integrity="{wrong_hash}">'
            html_file.write_text(html_content)
            
            validator = SRIValidator()
            result = validator.validate_html_file(html_file)
            
            assert result['valid'] == 0
            assert result['invalid'] == 1
            assert result['assets'][0]['status'] == 'invalid'
    
    def test_validate_html_file_no_sri(self):
        """Test validating HTML file with no SRI hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            html_file = tmppath / "index.html"
            html_content = '<link rel="stylesheet" href="style.css">'
            html_file.write_text(html_content)
            
            validator = SRIValidator()
            result = validator.validate_html_file(html_file)
            
            assert result['valid'] == 0
            assert result['invalid'] == 0
            assert len(result['assets']) == 0
    
    def test_validate_directory(self):
        """Test validating directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            css_content = b"body { margin: 0; }"
            css_file = tmppath / "style.css"
            css_file.write_bytes(css_content)
            
            correct_hash = calculate_sri_hash(css_content, 'sha384')
            
            for i in range(2):
                html_file = tmppath / f"test{i}.html"
                html_content = f'<link rel="stylesheet" href="style.css" integrity="{correct_hash}">'
                html_file.write_text(html_content)
            
            validator = SRIValidator()
            results = validator.validate_directory(tmppath)
            
            assert len(results) == 2
            assert all(r['valid'] == 1 for r in results)
