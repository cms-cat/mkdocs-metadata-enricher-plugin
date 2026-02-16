# Development Guide

This guide will help you set up a development environment and contribute to the mkdocs-metadata-enricher-plugin project.

## Prerequisites

- **Python** 3.9 or later
- **uv** package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git** (for version control and testing)
- **pre-commit** (installed via dev dependencies)

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/cms-cat/mkdocs-metadata-enricher-plugin.git
cd mkdocs-metadata-enricher-plugin
```

### 2. Initialize the Development Environment

```bash
# Install development dependencies
uv sync --all-extras

# Initialize pre-commit hooks (prek is a drop-in replacement for pre-commit)
prek install
# Or if you prefer the traditional pre-commit:
# pre-commit install
```

### 3. Verify Setup

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run formatting check
uv run ruff format --check .

# Run all pre-commit/prek checks
prek run --all-files
# Or with traditional pre-commit:
# pre-commit run --all-files
```

## Making Changes

### Code Style

The project uses **ruff** for linting and formatting. All code is automatically formatted using:

```bash
uv run ruff format .
```

And checked with:

```bash
uv run ruff check . --fix
```

These are also run automatically via pre-commit hooks when you commit.

### Writing Code

- Use **type hints** for all function parameters and return values
- Write **docstrings** using Google style format
- Keep functions focused and well-documented
- Follow PEP 8 conventions

Example:

```python
def _format_date(self, dt: datetime, fmt: str) -> str:
    """
    Format a datetime object.

    Args:
        dt: The datetime to format.
        fmt: The format string to use.

    Returns:
        The formatted date string.
    """
    return dt.strftime(fmt)
```

### Adding Tests

All new features should include tests. Tests go in the `tests/` directory and follow naming convention `test_*.py`.

**Unit tests** (in `test_plugin.py`):
- Test individual functions and methods in isolation
- Use mocking for external dependencies (git, filesystem)
- Mark with `@pytest.mark.unit`

**Integration tests** (in `test_integration.py`):
- Test with actual MkDocs builds
- Verify end-to-end behavior
- Mark with `@pytest.mark.integration`

Run tests with:

```bash
# All tests
uv run pytest

# Only unit tests
uv run pytest -m unit

# Only integration tests
uv run pytest -m integration

# With coverage report
uv run pytest --cov=src/mkdocs_metadata_enricher_plugin
```

## Project Structure

```
mkdocs-metadata-enricher-plugin/
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
├── .pre-commit-config.yaml  # Pre-commit hook configuration
├── src/
│   └── mkdocs_metadata_enricher_plugin/
│       ├── __init__.py      # Version export
│       ├── plugin.py        # Main plugin code
│       └── py.typed         # PEP 561 marker
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_plugin.py       # Unit tests
│   └── test_integration.py  # Integration tests
├── pyproject.toml           # Project configuration
├── README.md                # User documentation
├── DEVELOPMENT.md           # This file
├── CHANGELOG.md             # Release notes
└── LICENSE                  # MIT license
```

## Building and Publishing

### Build the Package

```bash
uv build
```

This creates:
- `dist/*.whl` - Python wheel (binary package)
- `dist/*.tar.gz` - Source distribution

### Testing the Build

```bash
# Install in editable mode for testing
uv pip install -e .

# Test with a sample mkdocs project
cd /tmp && mkdir test-site && cd test-site
# ... create mkdocs.yml and docs ...
mkdocs build
```

### Publishing to PyPI

Publishing is automated using GitHub Actions. To release a new version:

1.  **Trigger Release Preparation**:
    - Go to the **Actions** tab in GitHub.
    - Select the **Prepare Release** workflow.
    - Click **Run workflow** and choose the bumping strategy (patch, minor, or major).
    - This will automatically:
        - Bump the version in `src/mkdocs_metadata_enricher_plugin/__init__.py`.
        - Update `CHANGELOG.md` using `git-cliff`.
        - Create a new Pull Request titled `release: vX.Y.Z`.

2.  **Review and Merge**:
    - Review the generated PR and ensuring the changelog looks correct.
    - Merge the PR into `main`.

3.  **Automatic Tagging and Publishing**:
    - Once the PR is merged, the **Tag Release** workflow triggers.
    - It creates and pushes a git tag (e.g., `v0.2.0`).
    - This tag push automatically triggers the **Publish** workflow, which:
        - Builds the package.
        - Runs tests.
        - Publishes to PyPI using trusted publishing.

**Note**: First-time setup requires configuring PyPI trusted publishers:
- Go to [PyPI project settings](https://pypi.org/manage/project/mkdocs-metadata-enricher-plugin/settings/)
- Add a trusted publisher for the GitHub repo with environment name `pypi`

## Useful Commands

### Running Pre-Commit Checks Manually

```bash
# With prek (preferred, faster)
prek run --all-files

# Or with traditional pre-commit
pre-commit run --all-files
```

### Formatting Code

```bash
# Auto-format all files
uv run ruff format .

# Check without modifying
uv run ruff format --check .
```

### Linting

```bash
# Check for issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix
```

### Running Tests with Options

```bash
# Verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Show print statements
uv run pytest -s

# Run specific test
uv run pytest tests/test_plugin.py::TestPluginConfig::test_default_config

# Run tests matching pattern
uv run pytest -k "format"
```

### Debugging

```bash
# Enable logging during tests
uv run pytest -v -s --log-cli-level=DEBUG

# Drop to debugger on failure
uv run pytest --pdb

# Drop to debugger on first exception
uv run pytest --pdbcls=IPython.terminal.debugger:TerminalPdb
```

## Version Management

Version is stored in a single place: `src/mkdocs_metadata_enricher_plugin/__init__.py`

```python
__version__ = "0.1.0"
```

The build system (`hatchling`) automatically extracts this for:
- Package metadata in built distributions
- PyPI versioning

## Common Issues

### Pre-commit/prek hook fails

If hooks fail on commit, just run:
```bash
prek run --all-files
```

Then review and commit the fixes.

### Tests fail on import

Make sure dependencies are installed:
```bash
uv sync --all-extras
```

### Git date extraction issues

The plugin requires git history. If testing with new files:
```bash
git add tests/fixtures/
git commit -m "Add test fixtures"
```

### Timezone issues in tests

Tests use UTC and mocked git dates. If tests fail with timezone errors, ensure `pytz` is installed:
```bash
uv sync --all-extras
```

## Documentation

User documentation is in [README.md](https://github.com/cms-cat/mkdocs-metadata-enricher-plugin/blob/main/README.md). This file (DEVELOPMENT.md) covers development setup.

To improve documentation:
1. Edit the relevant file
2. Run local build (if applicable) to preview
3. Commit and test

## Getting Help

- Check existing [GitHub issues](https://github.com/cms-cat/mkdocs-metadata-enricher-plugin/issues)
- Read the [README](https://github.com/cms-cat/mkdocs-metadata-enricher-plugin/blob/main/README.md) for usage examples
- Review test cases in `tests/` for implementation examples

## Next Steps

After setup, try:

1. **Make a small change**:
   - Fix a typo in README.md
   - Run tests to ensure nothing breaks
   - Commit with a clear message

2. **Add a feature**:
   - Write a test first (TDD)
   - Implement the feature
   - Ensure all tests pass
   - Add documentation

3. **Submit a pull request**:
   - Fork the repo
   - Create a feature branch: `git checkout -b feature/my-feature`
   - Make changes and commit
   - Push and open a PR

Thank you for contributing! 🎉
