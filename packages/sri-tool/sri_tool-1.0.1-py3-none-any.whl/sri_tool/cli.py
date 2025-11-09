"""Command-line interface for SRI Tool."""

import sys
import argparse
import json
from pathlib import Path

from . import __version__
from .generator import SRIGenerator
from .validator import SRIValidator
from .utils import calculate_sri_hash, fetch_remote_content, is_remote_url


def cmd_generate(args):
    """Handle the generate command."""
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1
    
    generator = SRIGenerator(
        algorithm=args.algorithm,
        algorithms=args.algorithms if args.algorithms else [args.algorithm],
        verbose=args.verbose,
        dry_run=args.dry_run,
        backup=args.backup,
        update_existing=args.update,
        remove_existing=args.remove,
        add_crossorigin=not args.no_crossorigin
    )
    
    try:
        if path.is_file():
            generator.process_html_file(path)
        else:
            generator.scan_directory(path, recursive=args.recursive)
        
        generator.print_summary()
        
        return 1 if generator.errors else 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        return 1


def cmd_validate(args):
    """Handle the validate command."""
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1
    
    validator = SRIValidator(verbose=args.verbose)
    
    try:
        if path.is_file():
            result = validator.validate_html_file(path)
            results = [result]
        else:
            results = validator.validate_directory(path, recursive=args.recursive)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            validator.print_summary()
        
        has_invalid = any(r['invalid'] > 0 for r in results)
        return 1 if has_invalid else 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        return 1


def cmd_hash(args):
    """Handle the hash command."""
    try:
        if args.url:
            if not is_remote_url(args.url):
                print(f"Error: Invalid URL: {args.url}", file=sys.stderr)
                return 1
            
            print(f"Fetching: {args.url}")
            content = fetch_remote_content(args.url, timeout=args.timeout)
            if content is None:
                print(f"Error: Failed to fetch URL", file=sys.stderr)
                return 1
        elif args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File does not exist: {file_path}", file=sys.stderr)
                return 1
            content = file_path.read_bytes()
        else:
            print("Reading from stdin... (Ctrl+D to finish)")
            content = sys.stdin.buffer.read()
        
        algorithms = args.algorithms if args.algorithms else [args.algorithm]
        
        if len(algorithms) == 1:
            sri_hash = calculate_sri_hash(content, algorithms[0])
            print(f"\nSRI Hash ({algorithms[0]}):")
            print(sri_hash)
        else:
            print(f"\nSRI Hashes:")
            for algo in algorithms:
                sri_hash = calculate_sri_hash(content, algo)
                print(f"  {algo}: {sri_hash}")
        
        if args.html and args.url:
            print(f"\nHTML Tag:")
            sri_hash = calculate_sri_hash(content, algorithms[0])
            
            url_lower = args.url.lower()
            if url_lower.endswith('.css'):
                print(f'<link rel="stylesheet" href="{args.url}" integrity="{sri_hash}" crossorigin="anonymous">')
            elif url_lower.endswith('.js'):
                print(f'<script src="{args.url}" integrity="{sri_hash}" crossorigin="anonymous"></script>')
            else:
                print(f'<!-- Add integrity="{sri_hash}" crossorigin="anonymous" to your tag -->')
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='sri-tool',
        description='Subresource Integrity (SRI) Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate SRI hashes for all HTML files in a directory
  sri-tool generate /path/to/project -r
  
  # Generate with specific algorithm
  sri-tool generate . --algorithm sha512 -r
  
  # Generate with multiple algorithms
  sri-tool generate . --algorithms sha384 sha512 -r
  
  # Update existing SRI hashes
  sri-tool generate . -r --update
  
  # Remove all SRI hashes
  sri-tool generate . -r --remove
  
  # Validate SRI hashes in HTML files
  sri-tool validate /path/to/project -r
  
  # Calculate SRI hash for a URL
  sri-tool hash --url https://cdn.example.com/file.js
  
  # Calculate SRI hash for a file
  sri-tool hash --file script.js
  
  # Generate HTML tag with SRI hash
  sri-tool hash --url https://cdn.example.com/file.js --html

For more information, visit: https://github.com/adasThePro/sri-tool
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True
    
    generate_parser = subparsers.add_parser(
        'generate',
        aliases=['gen', 'add'],
        help='Generate or update SRI hashes in HTML files',
        description='Generate or update SRI integrity hashes for assets in HTML files'
    )
    generate_parser.add_argument(
        'path',
        type=str,
        help='HTML file or directory to process'
    )
    generate_parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively'
    )
    generate_parser.add_argument(
        '-a', '--algorithm',
        choices=['sha256', 'sha384', 'sha512'],
        default='sha384',
        help='Hash algorithm to use (default: sha384)'
    )
    generate_parser.add_argument(
        '--algorithms',
        nargs='+',
        choices=['sha256', 'sha384', 'sha512'],
        help='Use multiple hash algorithms (space-separated)'
    )
    generate_parser.add_argument(
        '-b', '--backup',
        action='store_true',
        default=True,
        help='Create backup files (default: enabled)'
    )
    generate_parser.add_argument(
        '--no-backup',
        action='store_false',
        dest='backup',
        help='Do not create backup files'
    )
    generate_parser.add_argument(
        '-u', '--update',
        action='store_true',
        help='Update existing SRI hashes'
    )
    generate_parser.add_argument(
        '--remove',
        action='store_true',
        help='Remove all SRI hashes from HTML files'
    )
    generate_parser.add_argument(
        '--no-crossorigin',
        action='store_true',
        help='Do not add crossorigin attribute for remote resources'
    )
    generate_parser.add_argument(
        '--local-only',
        action='store_true',
        help='Only process local files, skip remote URLs'
    )
    generate_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    generate_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    generate_parser.set_defaults(func=cmd_generate)
    
    validate_parser = subparsers.add_parser(
        'validate',
        aliases=['verify', 'check'],
        help='Validate SRI hashes in HTML files',
        description='Verify that SRI hashes in HTML files match the actual asset content'
    )
    validate_parser.add_argument(
        'path',
        type=str,
        help='HTML file or directory to validate'
    )
    validate_parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively'
    )
    validate_parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    validate_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    hash_parser = subparsers.add_parser(
        'hash',
        aliases=['calc', 'calculate'],
        help='Calculate SRI hash for a file or URL',
        description='Calculate SRI hash for a specific file, URL, or stdin'
    )
    hash_group = hash_parser.add_mutually_exclusive_group()
    hash_group.add_argument(
        '--url',
        type=str,
        help='URL to fetch and calculate hash for'
    )
    hash_group.add_argument(
        '--file',
        type=str,
        help='Local file to calculate hash for'
    )
    hash_parser.add_argument(
        '-a', '--algorithm',
        choices=['sha256', 'sha384', 'sha512'],
        default='sha384',
        help='Hash algorithm to use (default: sha384)'
    )
    hash_parser.add_argument(
        '--algorithms',
        nargs='+',
        choices=['sha256', 'sha384', 'sha512'],
        help='Calculate multiple hashes (space-separated)'
    )
    hash_parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML tag with integrity attribute'
    )
    hash_parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout in seconds for URLs (default: 10)'
    )
    hash_parser.set_defaults(func=cmd_hash)
    
    args = parser.parse_args()
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
