# Subresource Integrity Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#)

A command-line tool for managing Subresource Integrity (SRI) hashes in HTML files. Generate, validate, update, and remove SRI integrity attributes for CSS and JavaScript assets effortlessly.

## Features

**Complete SRI Management**
- Generate SRI hashes for local and remote assets
- Validate existing SRI hashes
- Update outdated SRI hashes
- Remove SRI hashes when needed

**Flexible Operations**
- Process single files or entire directories
- Recursive directory scanning
- Support for remote CDN URLs
- Multiple hash algorithms (SHA-256, SHA-384, SHA-512)
- Multiple hashes per asset

**Safe and Reliable**
- Automatic backup creation
- Dry-run mode for testing
- Detailed operation statistics
- Comprehensive error handling

**Developer Friendly**
- Clean command-line interface
- JSON output support
- Verbose logging options
- Easy installation via pip

## Installation

### Using pip (Recommended)

```bash
pip install sri-tool
```

### From Source

```bash
git clone https://github.com/adasThePro/sri-tool.git
cd sri-tool
pip install -e .
```

### Manual Installation

```bash
git clone https://github.com/adasThePro/sri-tool.git
cd sri-tool
pip install -r requirements.txt
python3 sri-tool --help
```

## Quick Start

### Generate SRI Hashes

Add SRI hashes to all HTML files in a directory:

```bash
sri-tool generate /path/to/project -r
```

Process a single HTML file:

```bash
sri-tool generate index.html
```

### Remove SRI Hashes

Remove SRI hashes from all HTML files in a directory:

```bash
sri-tool generate /path/to/project -r --remove
```

Process a single HTML file:

```bash
sri-tool generate index.html --remove
```

### Validate SRI Hashes

Check if existing SRI hashes are valid:

```bash
sri-tool validate /path/to/project -r
```

### Calculate Hash for URL

Get SRI hash for a remote resource:

```bash
sri-tool hash --url https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
```

Generate complete HTML tag:

```bash
sri-tool hash --url https://cdn.example.com/script.js --html
```

## Commands

### `generate` - Generate/Update SRI Hashes

Generate or update SRI integrity hashes for assets in HTML files.

**Aliases:** `gen`, `add`

```bash
sri-tool generate <path> [options]
```

**Options:**
- `-r, --recursive` - Process directories recursively
- `-a, --algorithm {sha256,sha384,sha512}` - Hash algorithm (default: sha384)
- `--algorithms ALGO [ALGO ...]` - Use multiple hash algorithms
- `-b, --backup` - Create backup files (default: enabled)
- `--no-backup` - Do not create backup files
- `-u, --update` - Update existing SRI hashes
- `--remove` - Remove all SRI hashes
- `--no-crossorigin` - Don't add crossorigin attribute
- `--local-only` - Only process local files
- `-v, --verbose` - Enable verbose output
- `--dry-run` - Preview changes without modifying files

**Examples:**

```bash
# Generate with default SHA-384
sri-tool generate /path/to/project -r

# Use SHA-512 algorithm
sri-tool generate . --algorithm sha512 -r

# Use multiple algorithms
sri-tool generate . --algorithms sha384 sha512 -r

# Update existing hashes
sri-tool generate . -r --update

# Dry run to see what would change
sri-tool generate . -r --dry-run

# Remove all SRI hashes
sri-tool generate . -r --remove
```

### `validate` - Verify SRI Hashes

Validate that SRI hashes match actual asset content.

**Aliases:** `verify`, `check`

```bash
sri-tool validate <path> [options]
```

**Options:**
- `-r, --recursive` - Process directories recursively
- `-j, --json` - Output results in JSON format
- `-v, --verbose` - Enable verbose output

**Examples:**

```bash
# Validate all HTML files
sri-tool validate /path/to/project -r

# Validate with JSON output
sri-tool validate . -r --json

# Validate single file with verbose output
sri-tool validate index.html -v
```

### `hash` - Calculate SRI Hash

Calculate SRI hash for a file, URL, or stdin.

**Aliases:** `calc`, `calculate`

```bash
sri-tool hash [--url URL | --file FILE] [options]
```

**Options:**
- `--url URL` - URL to fetch and calculate hash for
- `--file FILE` - Local file to calculate hash for
- `-a, --algorithm {sha256,sha384,sha512}` - Hash algorithm (default: sha384)
- `--algorithms ALGO [ALGO ...]` - Calculate multiple hashes
- `--html` - Generate HTML tag with integrity attribute
- `--timeout SECONDS` - Request timeout for URLs (default: 10)

**Examples:**

```bash
# Calculate hash for a URL
sri-tool hash --url https://cdn.example.com/script.js

# Calculate hash for a local file
sri-tool hash --file script.js

# Generate HTML tag with SRI hash
sri-tool hash --url https://cdn.example.com/style.css --html

# Calculate multiple hashes
sri-tool hash --file script.js --algorithms sha384 sha512

# Read from stdin
cat script.js | sri-tool hash
```

## Use Cases

### 1. Secure Your Static Site

Add SRI hashes to all assets before deployment:

```bash
sri-tool generate ./dist -r --no-backup
```

### 2. Verify Production Assets

Ensure production assets haven't been tampered with:

```bash
sri-tool validate ./public -r --json > validation-report.json
```

### 3. Update After Asset Changes

Update SRI hashes after modifying your CSS/JS files:

```bash
sri-tool generate ./src -r --update
```

### 4. Add SRI to CDN Resources

Get SRI hash for a CDN resource you want to use:

```bash
sri-tool hash --url https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js --html
```

Output:
```html
<script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js" 
        integrity="sha384-vtXRMe3mGCbOeY7l30aIg8H9p3GdeSe4IFlP6G8JMa7o7lXvnz3GFKzPxzJdPfGK" 
        crossorigin="anonymous"></script>
```

### 5. CI/CD Integration

Validate SRI hashes in your CI pipeline:

```bash
#!/bin/bash
sri-tool validate ./dist -r
if [ $? -ne 0 ]; then
    echo "SRI validation failed!"
    exit 1
fi
```

## What is SRI?

Subresource Integrity (SRI) is a security feature that enables browsers to verify that files they fetch from CDNs or external sources haven't been tampered with. When you include an `integrity` attribute on `<script>` or `<link>` tags, browsers will refuse to execute the file if its hash doesn't match the expected value.

**Before (Vulnerable):**
```html
<script src="https://cdn.example.com/library.js"></script>
```

**After (Protected with SRI):**
```html
<script src="https://cdn.example.com/library.js" 
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```

If the CDN is compromised and serves a different file, the browser will block it!

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## Configuration

SRI Tool works out of the box without configuration. However, you can customize its behavior using command-line options.

### Common Workflows

**Development:**
```bash
# Use dry-run to test before making changes
sri-tool generate . -r --dry-run -v
```

**Production:**
```bash
# Generate with backups disabled and SHA-512 for stronger security
sri-tool generate ./dist -r --no-backup --algorithm sha512
```

**Continuous Integration:**
```bash
# Validate in CI with verbose output and fail on error
sri-tool validate ./build -r -v || exit 1
```

## Advanced Features

### Multiple Hash Algorithms

For maximum compatibility, you can generate multiple hashes:

```bash
sri-tool generate . --algorithms sha384 sha512 -r
```

This creates:
```html
<script src="script.js" 
        integrity="sha384-hash1 sha512-hash2" 
        crossorigin="anonymous"></script>
```

Browsers will use the strongest algorithm they support.

### Processing Exclusions

Use dry-run mode to preview changes before applying them:

```bash
sri-tool generate . -r --dry-run -v
```

### Local-Only Mode

Skip remote URLs and only process local files:

```bash
sri-tool generate . -r --local-only
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ for web security