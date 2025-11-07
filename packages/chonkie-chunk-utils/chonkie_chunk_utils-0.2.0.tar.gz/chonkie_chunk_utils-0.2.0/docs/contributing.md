# Contributing

Thank you for your interest in contributing to `chonkie-chunk-utils`!

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**. Contributions should align with research goals and may be subject to significant changes.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/devcomfort/chonkie-chunk-utils.git
cd chonkie-chunk-utils
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

Or using Rye:
```bash
rye sync --dev
```

3. Run tests:
```bash
pytest
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings in NumPy style
- Keep functions focused and single-purpose

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting
- Use descriptive test names
- Include edge cases in tests

## Documentation

- Update relevant documentation when adding features
- Follow NumPy docstring style
- Include examples in docstrings
- Update README.md if needed

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

## Reporting Issues

When reporting issues, please include:

- Python version
- Library version
- Minimal reproducible example
- Expected behavior
- Actual behavior
- Error messages (if any)

## Research Focus Areas

Current research focuses on:

- Optimal chunk merging strategies
- Format effectiveness for LLM understanding
- Token optimization techniques
- Context quality improvements

Contributions in these areas are especially welcome!

## Questions?

Feel free to open an issue for questions or discussions.

