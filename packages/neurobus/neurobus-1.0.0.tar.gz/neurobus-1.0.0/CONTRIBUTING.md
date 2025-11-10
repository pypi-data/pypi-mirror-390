# Contributing to NeuroBUS

Thank you for your interest in contributing to NeuroBUS! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/tiverse-labs/neurobus/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Code sample or test case

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/tiverse-labs/neurobus/issues) and [Discussions](https://github.com/tiverse-labs/neurobus/discussions)
2. Create a new issue or discussion with:
   - Clear description of the enhancement
   - Use cases and benefits
   - Potential implementation approach

### Pull Requests

1. **Fork the repository** and create a branch from `main`
2. **Follow the development setup** instructions below
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality (maintain >90% coverage)
5. **Update documentation** if needed
6. **Run tests and linting** before submitting
7. **Submit a pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes (if applicable)

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/tiverse-labs/neurobus.git
cd neurobus

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=neurobus --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_core/test_bus.py

# Run integration tests
poetry run pytest tests/integration/

# Run performance tests
poetry run pytest tests/performance/ -v
```

### Code Quality

```bash
# Format code with black
poetry run black neurobus tests

# Lint with ruff
poetry run ruff check neurobus tests

# Type check with mypy
poetry run mypy neurobus

# Run all checks
poetry run black neurobus tests && poetry run ruff check neurobus tests && poetry run mypy neurobus
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 100)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use [mypy](http://mypy-lang.org/) for type checking (strict mode)

### Type Hints

- **100% type hint coverage required**
- Use type hints for all function arguments and return values
- Use generics where appropriate

```python
def process_event(event: Event) -> None:
    """Process an event."""
    ...

async def fetch_data(url: str) -> dict[str, Any]:
    """Fetch data from URL."""
    ...
```

### Docstrings

- Use Google-style docstrings
- Document all public APIs
- Include examples for complex functions

```python
def validate_topic(topic: str) -> None:
    """
    Validate event topic format.
    
    Topics must be non-empty strings containing only alphanumeric
    characters, dots, hyphens, and underscores.
    
    Args:
        topic: Topic string to validate
        
    Raises:
        ValidationError: If topic is invalid
        
    Example:
        >>> validate_topic("user.login")  # OK
        >>> validate_topic("")  # Raises ValidationError
    """
    ...
```

### Testing

- Maintain >90% test coverage
- Write unit tests for all new functionality
- Add integration tests for end-to-end flows
- Use descriptive test names

```python
async def test_bus_publishes_event_to_matching_subscribers():
    """Test that bus publishes events to all matching subscribers."""
    # Arrange
    bus = NeuroBus()
    received = []
    
    @bus.subscribe("test")
    async def handler(event: Event):
        received.append(event)
    
    # Act
    async with bus:
        await bus.publish(Event(topic="test"))
        await asyncio.sleep(0.01)
    
    # Assert
    assert len(received) == 1
```

### Commits

- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issues in commits (`Fixes #123`)
- Keep commits focused and atomic

```
Add semantic routing to subscription registry

- Implement similarity matching algorithm
- Add embedding cache for performance
- Update tests for new functionality

Closes #42
```

## Project Structure

```
neurobus/
├── neurobus/          # Source code
│   ├── core/          # Core event bus
│   ├── semantic/      # Semantic routing
│   ├── config/        # Configuration
│   └── utils/         # Utilities
├── tests/             # Test suite
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── performance/   # Performance tests
├── examples/          # Example applications
└── docs/              # Documentation
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for all public APIs
- Create examples for new features
- Update architecture docs for significant changes

## Review Process

1. All PRs require at least one review
2. CI must pass (tests, linting, type checking)
3. Coverage must remain >90%
4. Documentation must be updated

## Release Process

(For maintainers)

1. Update VERSION file
2. Update CHANGELOG.md
3. Create git tag
4. Build and publish to PyPI
5. Create GitHub release

## Getting Help

- [GitHub Discussions](https://github.com/tiverse-labs/neurobus/discussions) - Questions and discussions
- [GitHub Issues](https://github.com/tiverse-labs/neurobus/issues) - Bug reports and features
- Email: eshanized@proton.me

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- README.md for major features

Thank you for contributing to NeuroBUS! 🧠✨
