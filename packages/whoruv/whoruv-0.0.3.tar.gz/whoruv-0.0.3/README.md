# whoruv

[![PyPI - Version](https://img.shields.io/pypi/v/whoruv.svg)](https://pypi.org/project/whoruv)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/whoruv.svg)
![Last Commit](https://img.shields.io/github/last-commit/heiwa4126/whoruv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](https://github.com/heiwa4126/whoruv/blob/main/README-ja.md)

## Overview

A package that displays the following information when installed and executed with [Astral's uv](https://docs.astral.sh/uv/) using `uvx` or `uv tool install`:

- Python version
- Python executable path
- Script path

Created to understand the effects of uv's `--python` option.

## Usage Examples

```console
$ uvx whoruv

Installed 1 package in 3ms
Python Version: 3.12.12 (main, Oct 28 2025, 12:10:49) [Clang 20.1.4 ]
Executable Path: /home/user1/.cache/uv/archive-v0/VEm-1_LGBHubU7SZHYbs2/bin/python
Script Path: /home/user1/.cache/uv/archive-v0/VEm-1_LGBHubU7SZHYbs2/lib/python3.12/site-packages/whoruv/whoruv.py

$ uvx --python 3.10 whoruv

Installed 1 package in 3ms
Python Version: 3.10.12 (main, Aug 15 2025, 14:32:43) [GCC 11.4.0]
Executable Path: /home/user1/.cache/uv/archive-v0/Vcsgj4kD85VznE7HmFNsb/bin/python
Script Path: /home/user1/.cache/uv/archive-v0/Vcsgj4kD85VznE7HmFNsb/lib/python3.10/site-packages/whoruv/whoruv.py

$ uv tool install whoruv && whoruv

Resolved 1 package in 1ms
Installed 1 package in 3ms
 + whoruv==0.0.1
Installed 1 executable: whoruv
Python Version: 3.12.12 (main, Oct 28 2025, 12:10:49) [Clang 20.1.4 ]
Executable Path: /home/user1/.local/share/uv/tools/whoruv/bin/python
Script Path: /home/user1/.local/share/uv/tools/whoruv/lib/python3.12/site-packages/whoruv/whoruv.py

$ uv tool install --python 3.10 whoruv && whoruv

Ignoring existing environment for `whoruv`: the requested Python interpreter does not match the environment interpreter
Resolved 1 package in 1ms
Installed 1 package in 4ms
 + whoruv==0.0.1
Installed 1 executable: whoruv
Python Version: 3.10.12 (main, Aug 15 2025, 14:32:43) [GCC 11.4.0]
Executable Path: /home/user1/.local/share/uv/tools/whoruv/bin/python
Script Path: /home/user1/.local/share/uv/tools/whoruv/lib/python3.10/site-packages/whoruv/whoruv.py
```

## Development

### Setup

```bash
uv sync
```

### Task Execution

```bash
# Run tests
poe test

# Lint and format
poe check
poe format

# Type check
poe mypy

# Run all checks & build & smoke test
poe build
```

### Development Requirements

- Python >= 3.12
- uv

## License

MIT
