# Contributing to QuickInsights

Thank you for your interest in contributing to QuickInsights! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip or conda

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/quickinsights.git
   cd quickinsights
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/originalusername/quickinsights.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n quickinsights python=3.9
conda activate quickinsights
```

### 2. Install Dependencies

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or install all optional dependencies
pip install -e ".[dev,fast,gpu,cloud,profiling]"
```

### 3. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit pull requests
- **Documentation**: Improve docs and examples
- **Testing**: Add tests or improve test coverage
- **Code Review**: Review pull requests
- **Community**: Help other users

### Before Contributing

1. **Check existing issues**: Search for similar issues or feature requests
2. **Discuss major changes**: Open an issue to discuss significant changes
3. **Follow the roadmap**: Check our development roadmap for priorities

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: Use isort
- **Code formatting**: Use Black
- **Type hints**: Use mypy for type checking

### Code Formatting

```bash
# Format code with Black
black src/quickinsights/

# Sort imports with isort
isort src/quickinsights/

# Check types with mypy
mypy src/quickinsights/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=quickinsights --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v

# Run tests without warnings (recommended for clean output)
pytest -W ignore

# Alternative: Run with specific warning suppression
pytest -W ignore::DeprecationWarning -W ignore::FutureWarning -W ignore::UserWarning

# Run specific test class
pytest tests/test_core.py::TestCore

# Run specific test method
pytest tests/test_core.py::TestCore::test_validate_dataframe_basic

# Run tests with markers
pytest -m "not slow"  # Skip slow tests
pytest -m unit         # Run only unit tests
pytest -m integration  # Run only integration tests
```

### Test Structure

Our test suite is organized as follows:

- **`tests/conftest.py`**: Common fixtures and configuration
- **`tests/test_core.py`**: Core module tests (unit tests)
- **`tests/test_quick_insights.py`**: Quick insights module tests (unit tests)
- **`tests/test_smart_cleaner.py`**: Smart cleaner module tests (unit tests)
- **`tests/test_easy_start.py`**: Easy start module tests (integration tests)
- **`tests/test_dashboard.py`**: Dashboard module tests (integration tests)

### Test Categories

- **Unit Tests** (`@pytest.mark.unit`): Test individual functions/methods
- **Integration Tests** (`@pytest.mark.integration`): Test module interactions
- **Slow Tests** (`@pytest.mark.slow`): Tests that take longer to run

### Writing Tests

- Write tests for new features
- Ensure test coverage is maintained
- Use descriptive test names
- Follow pytest best practices
- Use fixtures from `conftest.py` for common test data
- Test both success and error cases
- Test edge cases (empty DataFrames, None values, etc.)

### Test Coverage

```bash
# Generate coverage report
pytest --cov=quickinsights --cov-report=html --cov-report=term

# View coverage in browser
# Open htmlcov/index.html in your browser
```

### Running Tests in CI

Tests are automatically run in CI/CD pipeline:
- All tests must pass before merging
- Coverage reports are generated
- Performance benchmarks are tracked

## Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Update documentation when changing code
- Follow Google-style docstrings

### Docstring Format

```python
def analyze_data(df: pd.DataFrame, save_plots: bool = True) -> dict:
    """
    Analyze the given dataframe and return comprehensive insights.
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyze
    save_plots : bool, default=True
        Whether to save generated plots
        
    Returns
    -------
    dict
        Dictionary containing analysis results
        
    Examples
    --------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> results = analyze_data(df)
    """
    pass
```

## Pull Request Process

### Creating a Pull Request

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a pull request** on GitHub

### Pull Request Guidelines

- Provide a clear description of changes
- Include relevant issue numbers
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

## Continuous Integration/Continuous Deployment (CI/CD)

### GitHub Actions

Our CI/CD pipeline automatically runs on every push and pull request:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest --cov=quickinsights --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### CI Checks

Before merging, the following must pass:

### Note on Warnings

Some tests may show NumPy deprecation warnings from pandas internal usage. These are **not** from our code and can be safely ignored. To run tests without warnings:

```bash
# Suppress all warnings (recommended)
python -W ignore -m pytest

# Or use pytest with warning filters
pytest -W ignore
```

These warnings are from pandas dependencies and will be resolved in future pandas versions.

- ✅ **Tests**: All 68 tests must pass
- ✅ **Coverage**: Maintain minimum 20% coverage
- ✅ **Linting**: Code follows style guidelines
- ✅ **Type Checking**: mypy passes without errors
- ✅ **Documentation**: Docs build successfully

### Automated Testing

- **Unit Tests**: Fast tests for individual functions
- **Integration Tests**: Tests for module interactions
- **Performance Tests**: Benchmark critical functions
- **Coverage Reports**: Track code coverage trends

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in setup.py
2. **Update changelog** with new features/fixes
3. **Create release branch** and test thoroughly
4. **Merge to main** and create GitHub release
5. **Build and upload** to PyPI

## Getting Help

If you need help with contributing:

- Check existing documentation
- Search GitHub issues
- Ask questions in discussions
- Contact maintainers directly

## Recognition

Contributors will be recognized in:

- Project README
- Release notes
- Contributor statistics
- Special acknowledgments for significant contributions

Thank you for contributing to QuickInsights! Your contributions help make this library better for everyone.
