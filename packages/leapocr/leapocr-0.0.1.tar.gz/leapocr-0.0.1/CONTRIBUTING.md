# Contributing to LeapOCR Python SDK

Thank you for your interest in contributing to the LeapOCR Python SDK! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Git
- OpenAPI Generator (for code generation)
- Java 21+ (for OpenAPI Generator)

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/leapocr-python.git
   cd leapocr-python
   ```

2. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Verify setup**:
   ```bash
   # Run tests
   make test

   # Run linting
   make lint

   # Run type checking
   make type-check
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Your Changes

Follow these guidelines:

- **Code Style**: Follow PEP 8 and use type hints
- **Formatting**: Run `make format` before committing
- **Linting**: Fix all issues from `make lint`
- **Type Checking**: Fix all issues from `make type-check`
- **Tests**: Add tests for new functionality
- **Documentation**: Update docstrings and README if needed

### 3. Run Tests

```bash
# Run all checks
make check

# Run unit tests
make test

# Run tests with coverage
make test-cov

# Run integration tests (requires API key)
export LEAPOCR_API_KEY="your-key"
make test-integration
```

### 4. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in processing"
git commit -m "docs: update README examples"
git commit -m "test: add tests for error handling"
git commit -m "refactor: simplify retry logic"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots (if UI changes)
- Test results

## Code Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints for all functions
- Maximum line length: 100 characters
- Use `ruff` for formatting and linting

### Type Hints

```python
# Good
def process_document(file_path: str, options: ProcessOptions | None = None) -> JobResult:
    ...

# Bad
def process_document(file_path, options=None):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed. Explain what the function does,
    any important details, and edge cases.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        APIError: When API request fails
    """
    ...
```

### Error Handling

- Use specific exception types from `leapocr.errors`
- Include helpful error messages
- Add context to errors (job_id, file_path, etc.)

```python
# Good
if not job_id:
    raise ValidationError("Job ID cannot be empty", field="job_id")

# Bad
if not job_id:
    raise ValueError("Invalid input")
```

### Async/Await

- All I/O operations should be async
- Use `async with` for resource management
- Handle `asyncio.CancelledError` appropriately

```python
# Good
async with LeapOCR(api_key) as client:
    result = await client.ocr.process_file("document.pdf")

# Bad
client = LeapOCR(api_key)
result = client.ocr.process_file("document.pdf")  # Missing await
```

## Testing Guidelines

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Test both success and error cases

```python
class TestProcessFile:
    """Tests for process_file function."""

    async def test_process_valid_pdf(self):
        """Test processing a valid PDF file."""
        ...

    async def test_process_invalid_file_type(self):
        """Test error handling for invalid file types."""
        ...
```

### Test Coverage

- Aim for >90% code coverage
- Focus on critical paths
- Don't test generated code

### Running Tests

```bash
# Unit tests only
pytest tests/unit/

# With coverage
pytest tests/unit/ --cov=leapocr --cov-report=html

# Integration tests
export LEAPOCR_API_KEY="your-key"
pytest tests/integration/

# Specific test
pytest tests/unit/test_errors.py::TestLeapOCRError::test_basic_error
```

## Code Generation

If you need to regenerate the OpenAPI client:

```bash
# Fetch latest spec
make fetch-spec

# Regenerate client
make generate

# Or do both
make regenerate
```

Note: Generated code in `leapocr/generated/` should not be manually edited.

## Documentation

### Updating Documentation

- Update docstrings for code changes
- Update README.md for new features
- Add examples for new functionality
- Update CHANGELOG.md with changes

### Example Format

When adding examples:

```python
"""Example: Brief description.

This example demonstrates:
- Feature A
- Feature B
- Feature C

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
from leapocr import LeapOCR

async def main():
    async with LeapOCR("api-key") as client:
        # Example code here
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

## Pull Request Process

1. **Before Submitting**:
   - Run all checks: `make check`
   - Run tests: `make test`
   - Update documentation
   - Update CHANGELOG.md

2. **PR Description**:
   - Clear title and description
   - Link related issues
   - List changes made
   - Include test results

3. **Review Process**:
   - Address review comments
   - Keep commits clean and logical
   - Squash commits if needed

4. **After Approval**:
   - Maintainers will merge your PR
   - PR will be included in next release

## Common Tasks

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check

# Run tests
make test

# Run tests with coverage
make test-cov

# Build package
make build

# Clean build artifacts
make clean
```

## Release Process

See [RELEASING.md](RELEASING.md) for the release process (maintainers only).

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/leapocr/leapocr-python/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/leapocr/leapocr-python/issues)
- **Security**: Email security@leapocr.com
- **General**: Email support@leapocr.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in:
- GitHub contributors page
- Release notes
- README (for significant contributions)

Thank you for contributing! 🎉
