"""SRI hash generator for HTML files."""

import re
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
import logging

from .utils import (
    calculate_sri_hash,
    calculate_multiple_hashes,
    fetch_remote_content,
    resolve_asset_path,
    is_remote_url,
    is_data_uri,
    should_add_crossorigin
)


class SRIGenerator:
    """Generate and update SRI hashes in HTML files."""
    
    def __init__(self, 
                 algorithm: str = 'sha384',
                 algorithms: Optional[List[str]] = None,
                 verbose: bool = False,
                 dry_run: bool = False,
                 backup: bool = True,
                 update_existing: bool = False,
                 remove_existing: bool = False,
                 add_crossorigin: bool = True):
        """
        Initialize SRI Generator.
        
        Args:
            algorithm: Primary hash algorithm (sha256, sha384, sha512)
            algorithms: List of algorithms for multiple hashes
            verbose: Enable verbose output
            dry_run: Don't modify files
            backup: Create backup files
            update_existing: Update existing integrity attributes
            remove_existing: Remove integrity attributes
            add_crossorigin: Add crossorigin attribute for remote resources
        """
        self.algorithm = algorithm
        self.algorithms = algorithms or [algorithm]
        self.verbose = verbose
        self.dry_run = dry_run
        self.backup = backup
        self.update_existing = update_existing
        self.remove_existing = remove_existing
        self.add_crossorigin = add_crossorigin
        
        self.processed_files = 0
        self.modified_files = 0
        self.errors = []
        self.stats = {
            'assets_processed': 0,
            'assets_updated': 0,
            'assets_skipped': 0,
            'assets_removed': 0
        }
        
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_asset_content(self, html_file_path: Path, asset_path: str) -> Optional[bytes]:
        """
        Get content of an asset (local or remote).
        
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
    
    def process_html_content(self, html_content: str, html_file_path: Path) -> Tuple[str, int]:
        """
        Process HTML content and add/update/remove SRI hashes.
        
        Args:
            html_content: Original HTML content
            html_file_path: Path to the HTML file
            
        Returns:
            Tuple of (modified_content, number_of_changes)
        """
        modified_content = html_content
        changes = 0
        
        link_pattern = re.compile(
            r'<link\s+([^>]*?)>',
            re.IGNORECASE | re.DOTALL
        )
        
        script_pattern = re.compile(
            r'<script\s+([^>]*?)>',
            re.IGNORECASE | re.DOTALL
        )
        
        def extract_attribute(tag: str, attr: str) -> Optional[str]:
            """Extract attribute value from tag."""
            pattern = re.compile(rf'{attr}\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
            match = pattern.search(tag)
            return match.group(1) if match else None
        
        def has_attribute(tag: str, attr: str) -> bool:
            """Check if tag has an attribute."""
            pattern = re.compile(rf'{attr}\s*=', re.IGNORECASE)
            return pattern.search(tag) is not None
        
        def remove_attribute(tag: str, attr: str) -> str:
            """Remove an attribute from a tag."""
            pattern = re.compile(rf'\s*{attr}\s*=\s*["\'][^"\']*["\']', re.IGNORECASE)
            return pattern.sub('', tag)
        
        def process_tag(match, tag_type):
            nonlocal changes, modified_content
            
            full_tag = match.group(0)
            attrs = match.group(1)
            
            url_attr = 'href' if tag_type == 'link' else 'src'
            
            url = extract_attribute(full_tag, url_attr)
            if not url:
                return full_tag
            
            if is_data_uri(url):
                return full_tag
            
            self.stats['assets_processed'] += 1
            
            if self.remove_existing:
                if has_attribute(full_tag, 'integrity'):
                    new_tag = remove_attribute(full_tag, 'integrity')
                    new_tag = remove_attribute(new_tag, 'crossorigin')
                    new_tag = re.sub(r'\s+', ' ', new_tag)
                    new_tag = re.sub(r'\s+>', '>', new_tag)
                    self.logger.info(f"Removed SRI hash from: {url}")
                    changes += 1
                    self.stats['assets_removed'] += 1
                    return new_tag
                return full_tag
            
            has_integrity = has_attribute(full_tag, 'integrity')
            
            if has_integrity and not self.update_existing:
                self.logger.debug(f"Skipping {url} - integrity already present")
                self.stats['assets_skipped'] += 1
                return full_tag
            
            content = self.get_asset_content(html_file_path, url)
            if content is None:
                self.stats['assets_skipped'] += 1
                return full_tag
            
            if len(self.algorithms) > 1:
                hashes = calculate_multiple_hashes(content, self.algorithms)
                sri_value = ' '.join(hashes)
            else:
                sri_value = calculate_sri_hash(content, self.algorithm)
            
            if has_integrity:
                new_tag = remove_attribute(full_tag, 'integrity')
                new_tag = remove_attribute(new_tag, 'crossorigin')
            else:
                new_tag = full_tag
            
            new_tag = new_tag.rstrip('>').rstrip()
            new_tag += f' integrity="{sri_value}"'

            if self.add_crossorigin and should_add_crossorigin(url):
                new_tag += ' crossorigin="anonymous"'
            
            new_tag += '>'
            
            action = "Updated" if has_integrity else "Added"
            self.logger.info(f"{action} SRI hash for: {url}")
            changes += 1
            self.stats['assets_updated'] += 1
            
            return new_tag
        
        modified_content = link_pattern.sub(
            lambda m: process_tag(m, 'link') if extract_attribute(m.group(0), 'href') else m.group(0),
            modified_content
        )
        
        modified_content = script_pattern.sub(
            lambda m: process_tag(m, 'script') if extract_attribute(m.group(0), 'src') else m.group(0),
            modified_content
        )
        
        return modified_content, changes
    
    def process_html_file(self, file_path: Path) -> bool:
        """
        Process a single HTML file.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            True if file was modified, False otherwise
        """
        self.logger.info(f"Processing: {file_path}")
        self.processed_files += 1
        
        try:
            original_content = file_path.read_text(encoding='utf-8')
            
            modified_content, changes = self.process_html_content(
                original_content, 
                file_path
            )
            
            if changes == 0:
                self.logger.debug(f"No changes needed for {file_path}")
                return False
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would modify {file_path} ({changes} assets)")
                return True
            
            if self.backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                shutil.copy2(file_path, backup_path)
                self.logger.debug(f"Created backup: {backup_path}")
            
            file_path.write_text(modified_content, encoding='utf-8')
            action = "removed from" if self.remove_existing else "updated in"
            self.logger.info(f"Modified {file_path} ({changes} assets {action})")
            self.modified_files += 1
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def scan_directory(self, directory: Path, recursive: bool = False) -> None:
        """
        Scan directory for HTML files and process them.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
        """
        if not directory.is_dir():
            self.logger.error(f"Not a directory: {directory}")
            return
        
        self.logger.info(f"Scanning directory: {directory}")
        
        pattern = '**/*.html' if recursive else '*.html'
        html_files = list(directory.glob(pattern))
        
        if not html_files:
            self.logger.warning(f"No HTML files found in {directory}")
            return
        
        self.logger.info(f"Found {len(html_files)} HTML file(s)")
        
        for html_file in html_files:
            self.process_html_file(html_file)
    
    def print_summary(self) -> None:
        """Print processing summary."""
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Files processed:      {self.processed_files}")
        print(f"Files modified:       {self.modified_files}")
        print(f"Assets processed:     {self.stats['assets_processed']}")
        print(f"Assets updated:       {self.stats['assets_updated']}")
        print(f"Assets skipped:       {self.stats['assets_skipped']}")
        if self.remove_existing:
            print(f"Assets SRI removed:   {self.stats['assets_removed']}")
        print(f"Errors:               {len(self.errors)}")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.dry_run:
            print("\n[DRY RUN MODE] No files were actually modified.")
        
        print("="*70)
