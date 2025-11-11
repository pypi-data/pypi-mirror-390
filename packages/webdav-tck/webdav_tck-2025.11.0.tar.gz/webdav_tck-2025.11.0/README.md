# webdav_tck

A Python port of the [litmus](https://github.com/notroj/litmus) WebDAV server protocol compliance test suite.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL--2.0+-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-65%2F68-brightgreen.svg)](#implementation-status)

## Overview

webdav_tck is a WebDAV server protocol compliance test suite that validates server implementations against RFC 4918 (HTTP Extensions for Web Distributed Authoring and Versioning). This is a modern Python rewrite of the original C-based litmus test suite with async/await support and comprehensive test coverage.

**Key Highlights:**
- 🚀 Modern async Python implementation
- ✅ 65 tests covering WebDAV Class 1 & 2 operations
- 🎨 Rich colored terminal output
- 📊 Detailed test reporting and debug logging
- 🔒 Full locking support (exclusive/shared, conditional requests)
- 🌐 UTF-8 and Unicode support

## Features

- ✅ **Basic Operations**: OPTIONS, PUT, GET, MKCOL, DELETE
- ✅ **COPY/MOVE**: Resource and collection operations with Depth and Overwrite headers
- ✅ **Properties**: PROPFIND, PROPPATCH with custom and live properties
- ✅ **Locking**: WebDAV Class 2 locking (exclusive/shared, conditional requests)
- 🚧 **HTTP Protocol**: Advanced HTTP features (coming soon)
- 🚧 **Large Files**: 2GB+ file handling (coming soon)

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/fermigier/webdav_tck.git
cd webdav_tck

# Install dependencies
uv sync
```

### From PyPI (coming soon)

```bash
pip install webdav_tck
```

## Usage

### Command Line

```bash
# Basic usage
dav-tck http://localhost/webdav/

# With authentication
dav-tck http://localhost/webdav/ username password

# With HTTPS (ignore certificate errors)
dav-tck --insecure https://localhost/webdav/

# Quiet mode
dav-tck --quiet http://localhost/webdav/

# Run specific test suites
dav-tck --suites=basic,copymove,props,locks http://localhost/webdav/

# Use proxy
dav-tck --proxy=http://proxy.example.com:8080 http://localhost/webdav/
```

**Note**: The command is available as both `dav-tck` and `litmus` after installation.

### Options

- `--proxy, -p URL`: Use specified HTTP proxy
- `--system-proxy, -s`: Use system proxy configuration
- `--client-cert, -c FILE`: Use PKCS#12 client certificate
- `--insecure, -i`: Ignore TLS certificate verification failures
- `--quiet, -q`: Use abbreviated output format
- `--colour/--no-colour`: Force color output on/off (default: auto-detect)
- `--suites LIST`: Comma-separated list of test suites to run

## Test Suites

### Basic (✅ Implemented - 11 tests)

Tests fundamental HTTP and WebDAV operations:
- OPTIONS request and DAV header checking
- PUT/GET with byte-for-byte comparison
- UTF-8 characters in URIs
- MKCOL (create collection)
- DELETE (resources and collections)
- Error handling (409, 404, 415 status codes)

### COPY/MOVE (✅ Implemented - 7 tests)

Tests resource and collection operations:
- Simple COPY operations
- Overwrite behavior (Overwrite: T/F headers)
- Copying into non-existent collections (409 responses)
- Recursive collection copying (Depth: infinity)
- Shallow collection copying (Depth: 0)
- MOVE operations with lock handling
- Collection moves with members

### Properties (✅ Implemented - 11 tests)

Tests property manipulation:
- PROPFIND with various depths
- Invalid XML handling (400 responses)
- Setting custom properties via PROPPATCH
- Property persistence across MOVE
- Deleting and replacing properties
- Null namespace properties
- High Unicode character support (U+10000)
- Well-formed XML validation
- Live properties (getlastmodified)

### Locks (✅ Implemented - 36 tests)

Tests WebDAV Class 2 locking:
- Exclusive and shared locks
- Lock discovery via PROPFIND
- Lock refresh operations
- Owner vs non-owner access control
- Lock token management
- Conditional PUT with If: headers
- Complex conditional requests (lock token + ETag)
- Collection locking (Depth: infinity)
- Indirect lock refresh via collection members
- Lock-null resources (LOCK on unmapped URLs)
- Locks don't follow COPY operations

### Coming Soon

- **HTTP**: HTTP protocol compliance (Expect: 100-continue, etc.)
- **Large Files**: Handling files >2GB

## Development

### Setup

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy src/
uv run pyrefly src/

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Project Structure

```
webdav_tck/
├── src/webdav_tck/      # Main package
│   ├── framework/       # Test framework
│   │   ├── result.py    # Result types
│   │   ├── runner.py    # Test runner
│   │   └── suite.py     # Suite management
│   ├── suites/          # Test suites
│   │   ├── basic.py     # Basic operations (11 tests)
│   │   ├── copymove.py  # COPY/MOVE (7 tests)
│   │   ├── props.py     # Properties (11 tests)
│   │   └── locks.py     # Locking (36 tests)
│   ├── client.py        # WebDAV HTTP client
│   ├── session.py       # Session management
│   ├── xml_utils.py     # XML builders/parsers
│   └── __main__.py      # CLI entry point
├── tests/               # Unit tests
│   └── test_framework.py
└── pyproject.toml       # Project configuration
```

## Requirements

- Python 3.10+
- httpx (async HTTP client)
- lxml (XML processing)
- click (CLI interface)
- rich (colored output)

## Implementation Status

**Total: 65 tests implemented**

| Suite     | Tests | Status |
|-----------|-------|--------|
| basic     | 11    | ✅ Complete |
| copymove  | 7     | ✅ Complete |
| props     | 11    | ✅ Complete |
| locks     | 36    | ✅ Complete |
| http      | 1     | 🚧 Planned |
| largefile | 2     | 🚧 Planned |

**Progress: 65/68 tests (95.6%)**

## License

GNU General Public License v2.0 or later (GPL-2.0-or-later)

This maintains compatibility with the original litmus project.

## Credits

- Original litmus: Copyright (C) 1999-2025 Joe Orton
- Python port: Copyright (C) 2025 Abilian SAS and contributors

## Contributing

Contributions are welcome!

## References

- [Original litmus](https://github.com/notroj/litmus)
- [RFC 4918: WebDAV](https://datatracker.ietf.org/doc/html/rfc4918)
