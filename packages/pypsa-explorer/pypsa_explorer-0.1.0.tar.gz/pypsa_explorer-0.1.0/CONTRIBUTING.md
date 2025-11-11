# Contributing to PyPSA Explorer

Thank you for your interest in contributing to PyPSA Explorer! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in your interactions.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/pypsa-explorer.git
cd pypsa-explorer

# Add upstream remote
git remote add upstream https://github.com/openenergytransition/pypsa-explorer.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

We use the following tools for code quality:

- **Black**: Code formatting (line length: 125)
- **Ruff**: Linting and code quality checks
- **MyPy**: Static type checking

Format your code before committing:

```bash
# Format code
black src/ tests/
ruff format src/ tests/

# Check linting
ruff check src/ tests/ --fix

# Type checking
mypy src/
```

### Testing

Write tests for new features and bug fixes:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pypsa_explorer --cov-report=html

# Run specific test
pytest tests/test_app.py -v

# Run tests in watch mode (requires pytest-watch)
ptw
```

### Documentation

Update documentation for any user-facing changes:

- Update docstrings in code (Google style)
- Update README.md if needed
- Add examples for new features
- Update CHANGELOG.md

### Type Hints

All code should include type hints:

```python
def process_network(
    network: pypsa.Network,
    carriers: list[str],
    query: str | None = None,
) -> dict[str, Any]:
    """
    Process network data with optional filtering.

    Parameters
    ----------
    network : pypsa.Network
        The PyPSA network to process
    carriers : list[str]
        List of carrier names to include
    query : str | None
        Optional pandas query string for filtering

    Returns
    -------
    dict[str, Any]
        Processed network data
    """
    # Implementation
    pass
```

## Pull Request Process

### 1. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of your changes"
```

Follow these commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests where applicable
- First line should be concise (50 chars or less)

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to the [PyPSA Explorer repository](https://github.com/openenergytransition/pypsa-explorer)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - Describe the changes
   - Reference related issues
   - Include screenshots for UI changes
   - List any breaking changes
   - Confirm tests pass

### 4. Code Review

- Address review comments
- Push updates to the same branch
- Request re-review when ready

### 5. Merge

Once approved, a maintainer will merge your PR.

## What to Contribute

### Bug Reports

Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, package versions)
- Minimal code example if possible

### Feature Requests

Have an idea? Open an issue with:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Willingness to contribute

### Good First Issues

Look for issues labeled `good-first-issue` for beginner-friendly tasks.

### Priority Areas

We especially welcome contributions in:
- Additional visualization types
- Export functionality (PNG, PDF, CSV)
- Performance optimizations
- Documentation improvements
- Test coverage expansion
- Accessibility improvements

## Project Structure

```
pypsa-explorer/
├── src/pypsa_explorer/    # Main package code
│   ├── callbacks/         # Dash callbacks
│   ├── layouts/           # UI components
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
└── examples/              # Example scripts and notebooks
```

## Development Tips

### Running in Debug Mode

```python
from pypsa_explorer import run_dashboard

run_dashboard(debug=True)  # Enable hot-reloading
```

### Testing Callbacks

```python
from dash.testing.application_runners import import_app

def test_callback(dash_duo):
    app = import_app("pypsa_explorer.app")
    dash_duo.start_server(app)
    # Test interactions
```

### Adding New Visualizations

1. Add layout in `src/pypsa_explorer/layouts/tabs.py`
2. Add callback in `src/pypsa_explorer/callbacks/visualizations.py`
3. Register callback in `src/pypsa_explorer/callbacks/__init__.py`
4. Add tests in `tests/test_visualizations.py`

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `src/pypsa_explorer/__init__.py`
2. Update CHANGELOG.md
3. Create release branch: `git checkout -b release/vX.Y.Z`
4. Tag release: `git tag vX.Y.Z`
5. Push tag: `git push origin vX.Y.Z`
6. Build and publish to PyPI: `python -m build && twine upload dist/*`
7. Create GitHub release with changelog

## Questions?

- Open an issue for questions
- Join our [discussions](https://github.com/openenergytransition/pypsa-explorer/discussions)
- Contact the maintainers

Thank you for contributing to PyPSA Explorer! 🎉
