# Contributing to INIAMET

Thank you for your interest in contributing to INIAMET! This document provides guidelines and instructions for contributing to the project.

## 🚀 Quick Start

### Setting Up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/iniamet.git
   cd iniamet
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode with dev dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## 📋 Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://github.com/psf/black) for code formatting (line length: 100)
- Use [flake8](https://flake8.pycqa.org/) for linting
- Add type hints to all function signatures
- Write docstrings for all public functions (Google style)

**Format code before committing:**
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Docstring Format

Use Google-style docstrings:

```python
def download_data(station: str, variable: int, start_date: datetime) -> pd.DataFrame:
    """
    Download data from a specific station.
    
    Args:
        station: Station code (e.g., 'INIA-47')
        variable: Variable ID (e.g., 2002 for temperature)
        start_date: Start date for data download
        
    Returns:
        DataFrame with downloaded data
        
    Raises:
        ValueError: If station code is invalid
        APIError: If API request fails
        
    Example:
        >>> client = INIAClient()
        >>> data = client.get_data('INIA-47', 2002, datetime(2024, 9, 1))
    """
```

### Testing

- Write tests for all new features
- Maintain test coverage above 70%
- Use pytest for testing
- Place tests in `tests/` directory

**Run tests:**
```bash
pytest                          # Run all tests
pytest tests/test_api_client.py # Run specific test file
pytest --cov=iniamet           # Run with coverage report
pytest -v                       # Verbose output
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add support for hourly data aggregation
fix: handle missing data in temperature downloads
docs: update README with regional download examples
test: add tests for quality control module
```

## 🐛 Reporting Bugs

**Before submitting a bug report:**
1. Check existing issues to avoid duplicates
2. Verify the bug with the latest version
3. Collect relevant information (Python version, OS, error traceback)

**Bug report should include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Code snippet (minimal reproducible example)
- Error messages/traceback
- Environment details

## 💡 Suggesting Features

**Feature requests should include:**
- Clear description of the problem/use case
- Proposed solution or API design
- Example usage code
- Potential impact on existing functionality

## 🔧 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Reference related issues
   - Describe changes clearly
   - Include examples if applicable
   - Ensure all CI checks pass

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated (README, docstrings)
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or clearly documented)
- [ ] All CI checks passing

## 📁 Project Structure

```
iniamet-library/
├── src/iniamet/           # Main package
│   ├── __init__.py       # Package exports
│   ├── api_client.py     # Low-level API client
│   ├── client.py         # High-level INIAClient
│   ├── stations.py       # Station management
│   ├── data.py           # Data downloader
│   ├── regional.py       # Regional downloader
│   ├── qc.py             # Quality control
│   ├── visualization.py  # Mapping/plotting
│   ├── cache.py          # Caching system
│   └── utils.py          # Utility functions
├── tests/                # Test suite
├── examples/             # Example scripts
├── docs/                 # Documentation
└── README.md            # Main documentation
```

## 🧪 Adding New Features

### Adding a New Variable Type

1. Update `utils.py` with variable mapping
2. Add variable-specific validation in `qc.py`
3. Add tests in `tests/test_utils.py`
4. Update documentation with examples

### Adding Regional Features

1. Implement in `regional.py`
2. Add quality control if needed
3. Create example script in `examples/`
4. Add recipe to `docs/RECIPES.md`

## 📝 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples to `examples/` directory
- Add recipes to `docs/RECIPES.md`
- Update CHANGELOG.md

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Unprofessional conduct

## ❓ Questions?

- Open a [GitHub Discussion](https://github.com/yourusername/iniamet/discussions)
- Email: data@inia.cl (for general inquiries)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to INIAMET! 🌤️
