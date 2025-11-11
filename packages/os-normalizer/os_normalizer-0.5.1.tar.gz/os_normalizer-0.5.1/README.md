# OS Normalizer

A Python library for identifying and parsing operating system information from various sources.

## Overview

The OS Normalizer library parses raw operating system strings and supplimental data to identify the OS family, version, architecture, and other details. It supports parsing of:

- Windows (NT builds, versions)
- macOS (Darwin versions, codenames)
- Linux distributions (Ubuntu, Debian, Red Hat, etc.)
- iOS and Android mobile OS
- BSD variants (FreeBSD, OpenBSD, NetBSD)
- Network operating systems (Cisco IOS, Junos, FortiOS, etc.)

## Installation

```bash
pip install os-normalizer
```

## Usage

The main entry point is the `normalize_os` function, which takes a string and an optional data dictionary and returns a structured `OSData` result.

### Basic Usage

```python
from os_normalizer import normalize_os

# Parse the OS information
result = normalize_os("Windows NT 10.0 build 22631 Enterprise x64")
print(result.family)  # windows
print(result.product)  # Windows 11
print(result.version_major)  # 11
```

### Using OS Release Data

```python
from os_normalizer import normalize_os

# Fingerprint with both raw string and contents of os-release file
raw_os_string="Linux host 5.15.0-122-generic x86_64"
os_release_data={
    "os_release": 'NAME="Ubuntu"\nID=ubuntu\nVERSION_ID="22.04.4"\nVERSION_CODENAME=jammy\nPRETTY_NAME="Ubuntu 22.04.4 LTS"'
}

result = normalize_os(raw_os_string, os_release_data)
print(result.family)  # linux
print(result.product)  # Ubuntu
print(result.codename)  # Jammy
print(result.arch)  # x86_64
```

### Parsing Network Operating Systems

```python
from os_normalizer import normalize_os

# Parse Cisco IOS XE
raw_os_string="Cisco IOS XE Software, Version 17.9.4a (Amsterdam) C9300-24T, universalk9, c9300-universalk9.17.09.04a.SPA.bin"

result = normalize_os(raw_os_string)
print(result.family)  # network-os
print(result.vendor)  # Cisco
print(result.product)  # IOS XE
```

## Models

### OSData

Represents structured operating system information:

- `family`: OS family (windows, linux, macos, ios, android, bsd, network-os)
- `vendor`: Vendor name (Microsoft, Apple, Cisco, etc.)
- `product`: Product name (Windows 11, Ubuntu, macOS, etc.)
- `edition`: Edition information (Pro, Enterprise, etc.)
- `codename`: Release codename (Sequoia, Ventura, etc.)
- `channel`: Release channel (GA, LTS, etc.)
- `version_major`, `version_minor`, `version_patch`, `version_build`: Version components
- `kernel_name`, `kernel_version`: Kernel details
- `arch`: Architecture (x86_64, arm64, etc.)
- `distro`: Distribution name
- `like_distros`: List of similar distributions
- `pretty_name`: Pretty formatted name
- `hw_model`, `build_id`: Network device details
- `precision`: Precision level (family, product, major, minor, patch, build)
- `confidence`: Confidence score (0.0 to 1.0)
- `evidence`: Evidence used for parsing decisions
- `os_key`: Canonical key for deduplication

## Architecture

The library follows a modular architecture:

- **os_normalizer.py**: Main orchestration logic that delegates to appropriate parsers
- **parsers/**: OS-specific parsers (macOS, Linux, Windows, Network, Mobile, BSD)
- **models.py**: Data models for parsed results
- **constants.py**: Static lookup tables (aliases, build maps, codenames)
- **helpers.py**: Utility functions (architecture extraction, confidence calculation)

## Testing

You can run tests with uv in a few ways:

- Ephemeral runner (downloads pytest if needed):
  - `uvx pytest`
- Use the project environment and dev dependencies declared in `pyproject.toml`:
  - `uv run --group dev pytest`
- Optional editable install for import paths:
  - `uv pip install -e .`
  - `uv run pytest`

### Using Nox (with nox-uv)

If you prefer repeatable sessions, this project includes Nox configured with the `nox-uv` plugin so virtualenvs are created via `uv`:

- Run tests: `uv run nox`

## Contributing

Contributions are welcome! Please ensure that any new parsers or improvements follow the existing code patterns and include appropriate tests.

## License

MIT
