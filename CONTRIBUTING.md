# Contributing to Crypto MCP Server

Thank you for considering contributing to the Crypto MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-mcp-server.git
   cd crypto-mcp-server
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add docstrings to functions and classes
   - Update documentation as needed

4. **Write tests**
   - Add tests for new functionality
   - Ensure existing tests pass
   - Aim for >80% code coverage

5. **Run quality checks**
   ```bash
   # Format code
   black crypto_mcp_server tests
   isort crypto_mcp_server tests
   
   # Run linter
   flake8 crypto_mcp_server tests
   
   # Run tests
   pytest --cov=crypto_mcp_server
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Explain the changes made

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-mcp-server.git
   cd crypto-mcp-server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up pre-commit hooks** (optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Coding Standards

### Python Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Use type hints where appropriate
- Maximum function length: ~50 lines

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md for user-facing changes
- Add code comments for complex logic

### Testing

- Write unit tests for new functions
- Use pytest fixtures for common test data
- Mock external API calls
- Test edge cases and error conditions

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs when applicable

Examples:
```
Add caching for OHLCV data endpoints
Fix rate limiter not respecting time window
Update README with new installation steps
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=crypto_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_validators.py

# Run specific test
pytest tests/test_cache.py::TestCacheManager::test_cache_hit
```

### Writing Tests

```python
"""
Tests for new_module
"""

import pytest
from crypto_mcp_server.new_module import NewClass


class TestNewClass:
    """Tests for NewClass"""

    def setup_method(self):
        """Set up test fixtures"""
        self.instance = NewClass()

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = self.instance.method()
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ExpectedException):
            self.instance.method_that_fails()
```

## Project Structure

```
crypto-mcp-server/
├── crypto_mcp_server/    # Main package
│   ├── __init__.py
│   ├── server.py         # MCP server
│   ├── exchange.py       # Exchange connector
│   └── ...
├── tests/                # Test suite
│   ├── conftest.py       # Test fixtures
│   └── test_*.py         # Test files
├── examples/             # Usage examples
├── docs/                 # Documentation
└── ...
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release branch
4. Run all tests and quality checks
5. Create a pull request to main
6. Tag the release after merge

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions
- Contact maintainers

Thank you for contributing! 🎉
