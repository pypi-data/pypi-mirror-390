"""SRI hash validator."""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

from .utils import (
    calculate_sri_hash,
    fetch_remote_content,
    resolve_asset_path,
    is_remote_url,
    is_data_uri
)


class SRIValidator:
    """Validate SRI hashes in HTML files."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize SRI Validator.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.results = []
        
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_sri_info(self, html_content: str) -> List[Dict]:
        """
        Extract SRI information from HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of dictionaries with asset information
        """
        assets = []
        
        link_pattern = re.compile(
            r'<link\s+([^>]*?integrity\s*=\s*["\']([^"\']+)["\'][^>]*?)>',
            re.IGNORECASE | re.DOTALL
        )
        
        script_pattern = re.compile(
            r'<script\s+([^>]*?integrity\s*=\s*["\']([^"\']+)["\'][^>]*?)>',
            re.IGNORECASE | re.DOTALL
        )
        
        def extract_url(tag: str, attr: str) -> Optional[str]:
            pattern = re.compile(rf'{attr}\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
            match = pattern.search(tag)
            return match.group(1) if match else None
        
        for match in link_pattern.finditer(html_content):
            tag = match.group(1)
            integrity = match.group(2)
            url = extract_url(tag, 'href')
            if url:
                assets.append({
                    'type': 'stylesheet',
                    'url': url,
                    'integrity': integrity,
                    'tag': match.group(0)
                })
        
        for match in script_pattern.finditer(html_content):
            tag = match.group(1)
            integrity = match.group(2)
            url = extract_url(tag, 'src')
            if url:
                assets.append({
                    'type': 'script',
                    'url': url,
                    'integrity': integrity,
                    'tag': match.group(0)
                })
        
        return assets
    
    def get_asset_content(self, html_file_path: Path, asset_path: str) -> Optional[bytes]:
        """
        Get content of an asset.
        
        Args:
            html_file_path: Path to the HTML file
            asset_path: Asset path from HTML
            
        Returns:
            Asset content as bytes or None if not found
        """
        if is_remote_url(asset_path):
            return fetch_remote_content(asset_path, logger=self.logger)
        
        resolved_path = resolve_asset_path(html_file_path, asset_path)
        if resolved_path is None:
            self.logger.warning(f"Could not resolve asset: {asset_path}")
            return None
        
        try:
            return resolved_path.read_bytes()
        except Exception as e:
            self.logger.error(f"Failed to read {resolved_path}: {e}")
            return None
    
    def validate_integrity(self, content: bytes, expected_hash: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if content matches the expected SRI hash.
        
        Args:
            content: Asset content
            expected_hash: Expected SRI hash (e.g., "sha384-..." or multiple hashes separated by space)
            
        Returns:
            Tuple of (is_valid, actual_hash)
        """
        expected_hashes = expected_hash.split()
        
        for single_hash in expected_hashes:
            parts = single_hash.split('-', 1)
            if len(parts) != 2:
                continue
            
            algorithm = parts[0].lower()
            
            try:
                actual_hash = calculate_sri_hash(content, algorithm)
                if actual_hash == single_hash:
                    return True, actual_hash
            except ValueError as e:
                self.logger.debug(f"Error calculating hash with {algorithm}: {e}")
                continue
        
        if expected_hashes:
            parts = expected_hashes[0].split('-', 1)
            if len(parts) == 2:
                algorithm = parts[0].lower()
                try:
                    actual_hash = calculate_sri_hash(content, algorithm)
                    return False, actual_hash
                except ValueError:
                    pass
        
        return False, None
    
    def validate_html_file(self, file_path: Path) -> Dict:
        """
        Validate SRI hashes in an HTML file.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info(f"Validating: {file_path}")
        
        result = {
            'file': str(file_path),
            'assets': [],
            'valid': 0,
            'invalid': 0,
            'missing': 0,
            'errors': []
        }
        
        try:
            html_content = file_path.read_text(encoding='utf-8')
            assets = self.extract_sri_info(html_content)
            
            if not assets:
                self.logger.info(f"No SRI hashes found in {file_path}")
                return result
            
            self.logger.info(f"Found {len(assets)} asset(s) with SRI hashes")
            
            for asset in assets:
                asset_result = {
                    'type': asset['type'],
                    'url': asset['url'],
                    'expected_hash': asset['integrity'],
                    'status': 'unknown'
                }
                
                if is_data_uri(asset['url']):
                    asset_result['status'] = 'skipped'
                    result['assets'].append(asset_result)
                    continue
                
                content = self.get_asset_content(file_path, asset['url'])
                
                if content is None:
                    asset_result['status'] = 'error'
                    asset_result['message'] = 'Could not fetch asset content'
                    result['missing'] += 1
                    self.logger.warning(f"Could not validate {asset['url']}: content not available")
                else:
                    is_valid, actual_hash = self.validate_integrity(content, asset['integrity'])
                    
                    if is_valid:
                        asset_result['status'] = 'valid'
                        result['valid'] += 1
                        self.logger.info(f"✓ Valid: {asset['url']}")
                    else:
                        asset_result['status'] = 'invalid'
                        asset_result['actual_hash'] = actual_hash
                        result['invalid'] += 1
                        self.logger.error(f"✗ Invalid: {asset['url']}")
                        self.logger.error(f"  Expected: {asset['integrity']}")
                        if actual_hash:
                            self.logger.error(f"  Actual:   {actual_hash}")
                
                result['assets'].append(asset_result)
            
        except Exception as e:
            error_msg = f"Error validating {file_path}: {e}"
            self.logger.error(error_msg)
            result['errors'].append(error_msg)
        
        self.results.append(result)
        return result
    
    def validate_directory(self, directory: Path, recursive: bool = False) -> List[Dict]:
        """
        Validate SRI hashes in all HTML files in a directory.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of validation results
        """
        if not directory.is_dir():
            self.logger.error(f"Not a directory: {directory}")
            return []
        
        self.logger.info(f"Scanning directory: {directory}")
        
        pattern = '**/*.html' if recursive else '*.html'
        html_files = list(directory.glob(pattern))
        
        if not html_files:
            self.logger.warning(f"No HTML files found in {directory}")
            return []
        
        self.logger.info(f"Found {len(html_files)} HTML file(s)")
        
        results = []
        for html_file in html_files:
            result = self.validate_html_file(html_file)
            results.append(result)
        
        return results
    
    def print_summary(self) -> None:
        """Print validation summary."""
        if not self.results:
            print("No validation results available.")
            return
        
        total_files = len(self.results)
        total_assets = sum(len(r['assets']) for r in self.results)
        total_valid = sum(r['valid'] for r in self.results)
        total_invalid = sum(r['invalid'] for r in self.results)
        total_missing = sum(r['missing'] for r in self.results)
        total_errors = sum(len(r['errors']) for r in self.results)
        
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"Files validated:      {total_files}")
        print(f"Total assets:         {total_assets}")
        print(f"Valid hashes:         {total_valid}")
        print(f"Invalid hashes:       {total_invalid}")
        print(f"Missing/Error:        {total_missing}")
        print(f"File errors:          {total_errors}")
        
        if total_invalid > 0:
            print("\n⚠ WARNING: Some SRI hashes are invalid!")
        elif total_assets > 0:
            print("\n✓ All SRI hashes are valid!")
        
        print("="*70)
