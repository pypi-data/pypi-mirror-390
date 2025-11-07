# Installation

## Requirements

- Python >= 3.8
- chonkie >= 1.4.1

## Install from PyPI

```bash
pip install chonkie-chunk-utils
```

## Install using Rye

If you're using [Rye](https://rye-up.com/) for dependency management:

```bash
rye add chonkie-chunk-utils
```

## Install from Source

```bash
git clone https://github.com/devcomfort/chonkie-chunk-utils.git
cd chonkie-chunk-utils
pip install -e .
```

## Development Installation

For development, install with development dependencies:

```bash
git clone https://github.com/devcomfort/chonkie-chunk-utils.git
cd chonkie-chunk-utils
pip install -e ".[dev]"
```

Or using Rye:

```bash
rye sync --dev
```

## Verify Installation

You can verify the installation by importing the package:

```python
from chonkie_chunk_utils import sort_chunks, render_chunks
print("Installation successful!")
```

## Dependencies

The package depends on:

- `chonkie[all]>=1.4.1` - Core chunk management library
- `typing-extensions>=4.15.0` - Type hints support
- `loguru>=0.7.3` - Logging utilities
- `toolz>=1.1.0` - Functional programming utilities
- `toon-python>=0.1.2` - TOON format support

## Troubleshooting

### Import Errors

If you encounter import errors, make sure:

1. Python version is 3.8 or higher: `python --version`
2. All dependencies are installed: `pip list | grep chonkie`
3. Virtual environment is activated (if using one)

### Version Conflicts

If you have version conflicts with dependencies:

```bash
pip install --upgrade chonkie-chunk-utils
```

Or reinstall with specific versions:

```bash
pip install chonkie-chunk-utils --force-reinstall
```

