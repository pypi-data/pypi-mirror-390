"""Tests for SRI Generator."""

import tempfile
from pathlib import Path

from sri_tool.generator import SRIGenerator


class TestSRIGenerator:
    """Tests for SRIGenerator class."""
    
    def test_initialization(self):
        """Test generator initialization."""
        gen = SRIGenerator()
        assert gen.algorithm == 'sha384'
        assert gen.dry_run is False
        assert gen.backup is True
        assert gen.processed_files == 0
        assert gen.modified_files == 0
    
    def test_initialization_with_options(self):
        """Test generator initialization with custom options."""
        gen = SRIGenerator(
            algorithm='sha512',
            verbose=True,
            dry_run=True,
            backup=False
        )
        assert gen.algorithm == 'sha512'
        assert gen.verbose is True
        assert gen.dry_run is True
        assert gen.backup is False
    
    def test_process_simple_html(self):
        """Test processing simple HTML with local assets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_content = b"body { margin: 0; }"
            js_content = b"console.log('test');"
            
            css_file = tmppath / "style.css"
            js_file = tmppath / "script.js"
            html_file = tmppath / "index.html"
            
            css_file.write_bytes(css_content)
            js_file.write_bytes(js_content)
            
            html_content = '''<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
</head>
<body></body>
</html>'''
            html_file.write_text(html_content)
            
            gen = SRIGenerator(backup=False)
            result = gen.process_html_file(html_file)
            
            assert result is True
            assert gen.modified_files == 1

            modified = html_file.read_text()
            assert 'integrity=' in modified
            assert 'sha384-' in modified
    
    def test_dry_run_mode(self):
        """Test dry-run mode doesn't modify files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_file = tmppath / "style.css"
            html_file = tmppath / "index.html"
            
            css_file.write_bytes(b"body { margin: 0; }")
            html_content = '<link rel="stylesheet" href="style.css">'
            html_file.write_text(html_content)
            
            gen = SRIGenerator(dry_run=True, backup=False)
            gen.process_html_file(html_file)
            
            assert html_file.read_text() == html_content
    
    def test_backup_creation(self):
        """Test backup file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_file = tmppath / "style.css"
            html_file = tmppath / "index.html"
            backup_file = tmppath / "index.html.bak"
            
            css_file.write_bytes(b"body { margin: 0; }")
            html_content = '<link rel="stylesheet" href="style.css">'
            html_file.write_text(html_content)
            
            gen = SRIGenerator(backup=True)
            gen.process_html_file(html_file)
            
            assert backup_file.exists()
            assert backup_file.read_text() == html_content
    
    def test_skip_existing_integrity(self):
        """Test skipping tags that already have integrity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_file = tmppath / "style.css"
            html_file = tmppath / "index.html"
            
            css_file.write_bytes(b"body { margin: 0; }")
            html_content = '<link rel="stylesheet" href="style.css" integrity="sha384-existing">'
            html_file.write_text(html_content)
            
            gen = SRIGenerator(backup=False, update_existing=False)
            result = gen.process_html_file(html_file)
            
            assert result is False
            assert gen.stats['assets_skipped'] > 0
    
    def test_update_existing_integrity(self):
        """Test updating existing integrity attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            css_file = tmppath / "style.css"
            html_file = tmppath / "index.html"
            
            css_file.write_bytes(b"body { margin: 0; }")
            html_content = '<link rel="stylesheet" href="style.css" integrity="sha384-old">'
            html_file.write_text(html_content)
            
            gen = SRIGenerator(backup=False, update_existing=True)
            result = gen.process_html_file(html_file)
            
            assert result is True
            modified = html_file.read_text()
            assert 'integrity=' in modified
            assert 'sha384-old' not in modified
    
    def test_remove_mode(self):
        """Test removing integrity attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            html_file = tmppath / "index.html"
            html_content = '<link rel="stylesheet" href="style.css" integrity="sha384-hash" crossorigin="anonymous">'
            html_file.write_text(html_content)
            
            gen = SRIGenerator(backup=False, remove_existing=True)
            result = gen.process_html_file(html_file)
            
            assert result is True
            modified = html_file.read_text()
            assert 'integrity=' not in modified
            assert 'crossorigin=' not in modified
    
    def test_data_uri_skipped(self):
        """Test that data URIs are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            html_file = tmppath / "index.html"
            html_content = '<script src="data:text/javascript;base64,Y29uc29sZS5sb2c="></script>'
            html_file.write_text(html_content)
            
            gen = SRIGenerator(backup=False)
            result = gen.process_html_file(html_file)
            
            assert result is False
    
    def test_scan_directory(self):
        """Test scanning directory for HTML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            for i in range(3):
                html_file = tmppath / f"test{i}.html"
                css_file = tmppath / f"style{i}.css"
                css_file.write_bytes(b"body { margin: 0; }")
                html_file.write_text(f'<link rel="stylesheet" href="style{i}.css">')
            
            gen = SRIGenerator(backup=False)
            gen.scan_directory(tmppath, recursive=False)
            
            assert gen.processed_files == 3
            assert gen.modified_files == 3
