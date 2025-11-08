# Contributing to LionAGI QE Fleet

Thank you for your interest in contributing to LionAGI QE Fleet! We welcome contributions from the community, whether it's bug reports, feature requests, documentation improvements, or code contributions.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation Requirements](#documentation-requirements)
- [Community Guidelines](#community-guidelines)
- [Getting Help](#getting-help)

## Ways to Contribute

### 1. Report Bugs

If you find a bug, please [open an issue](https://github.com/lionagi/lionagi-qe-fleet/issues/new?template=bug_report.md) with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or screenshots

### 2. Request Features

Have an idea for a new feature? [Open a feature request](https://github.com/lionagi/lionagi-qe-fleet/issues/new?template=feature_request.md) with:
- Problem statement
- Proposed solution
- Alternative approaches considered
- Use cases and examples

### 3. Improve Documentation

Documentation improvements are always welcome:
- Fix typos or clarify unclear sections
- Add examples or tutorials
- Improve API documentation
- Translate documentation (if applicable)

[Open a documentation issue](https://github.com/lionagi/lionagi-qe-fleet/issues/new?template=documentation.md) or submit a PR directly.

### 4. Contribute Code

We welcome code contributions! See the sections below for our development workflow.

### 5. Help the Community

- Answer questions in GitHub Discussions
- Review pull requests
- Help triage issues
- Share your experiences and use cases

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Git

### Initial Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/lionagi-qe-fleet.git
   cd lionagi-qe-fleet
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/lionagi/lionagi-qe-fleet.git
   ```

4. **Create a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```bash
   # Install all dependencies including dev tools
   uv pip install -e ".[dev]"

   # Or install all optional dependencies
   uv pip install -e ".[all]"
   ```

6. **Verify installation**:
   ```bash
   pytest
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Run linters**:
   ```bash
   # Format code
   black src/ tests/

   # Check code style
   ruff check src/ tests/

   # Type checking
   mypy src/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   See [Commit Message Conventions](#commit-message-conventions) below.

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** on GitHub

## Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings (Black default)
- **Imports**: Organized by stdlib, third-party, local

### Type Hints

All functions and methods must have type hints:

```python
def process_test_result(
    test_name: str,
    result: TestResult,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """Process a test result and return metrics."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def execute_test_suite(
    suite: TestSuite,
    parallel: bool = False
) -> ExecutionResult:
    """Execute a test suite with optional parallel execution.

    Args:
        suite: The test suite to execute
        parallel: Whether to run tests in parallel

    Returns:
        ExecutionResult containing pass/fail status and metrics

    Raises:
        TestExecutionError: If test execution fails

    Example:
        >>> suite = TestSuite(tests=[...])
        >>> result = execute_test_suite(suite, parallel=True)
        >>> print(result.passed)
        True
    """
    ...
```

### Code Organization

- **Modules**: One concept per module
- **Classes**: Clear single responsibility
- **Functions**: Keep them small and focused
- **Comments**: Explain "why", not "what"

### Naming Conventions

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Prefix with `_`

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Add tests for new functionality
3. Update documentation
4. Run linters and formatters
5. Update CHANGELOG.md if applicable

### PR Template

When you open a PR, fill out the template with:

- **Description**: What does this PR do?
- **Type of Change**: Bug fix, feature, breaking change, docs
- **Testing**: What tests were added/updated?
- **Checklist**: Confirm all requirements met

### Review Process

1. **Automated checks** must pass (tests, linting)
2. **Code review** by maintainers
3. **Address feedback** if requested
4. **Approval** from at least one maintainer
5. **Merge** by maintainers

### After Merge

- Delete your feature branch
- Pull latest changes from upstream
- Close related issues if applicable

## Testing Requirements

### Writing Tests

- Use `pytest` for all tests
- Place tests in `tests/` directory matching `src/` structure
- Name test files `test_*.py`
- Name test functions `test_*`

### Test Structure

```python
import pytest
from lionagi_qe.agents.test_generator import TestGenerator

class TestTestGenerator:
    """Tests for TestGenerator agent."""

    @pytest.fixture
    def generator(self):
        """Create a test generator instance."""
        return TestGenerator()

    def test_generates_unit_tests(self, generator):
        """Test that generator creates valid unit tests."""
        result = generator.generate(type="unit", framework="pytest")
        assert result.tests is not None
        assert len(result.tests) > 0

    @pytest.mark.asyncio
    async def test_async_generation(self, generator):
        """Test async test generation."""
        result = await generator.generate_async(type="integration")
        assert result.success is True
```

### Test Coverage

- Aim for >80% code coverage
- All new features must have tests
- Bug fixes should include regression tests

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/lionagi_qe --cov-report=html

# Run specific test file
pytest tests/agents/test_test_generator.py

# Run specific test
pytest tests/agents/test_test_generator.py::TestTestGenerator::test_generates_unit_tests

# Run tests matching pattern
pytest -k "test_async"
```

## Documentation Requirements

### Code Documentation

- All public APIs must have docstrings
- Include examples in docstrings
- Document parameters, returns, and exceptions
- Keep docstrings up to date

### User Documentation

Update relevant docs when adding features:

- **README.md**: Quick start and overview
- **USAGE_GUIDE.md**: Detailed usage examples
- **docs/**: In-depth guides and API reference

### Examples

Add examples for new features:

- Place in `examples/` directory
- Include comments explaining key concepts
- Ensure examples run without errors

## Community Guidelines

### Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md). In summary:

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions
- **Discord**: Real-time chat (link TBD)

### Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(agents): add visual testing agent

Add new agent for visual regression testing with AI-powered
screenshot comparison.

Closes #123
```

```
fix(coverage): handle edge case in sublinear algorithm

Fix division by zero error when analyzing empty test suites.

Fixes #456
```

## Getting Help

### Documentation

- [README.md](README.md): Project overview
- [USAGE_GUIDE.md](USAGE_GUIDE.md): Detailed usage
- [docs/](docs/): API reference and guides

### Support Channels

1. **Search existing issues**: Someone may have had the same question
2. **GitHub Discussions**: Ask questions and discuss ideas
3. **GitHub Issues**: Report bugs or request features
4. **Discord**: Real-time community support (link TBD)

### Maintainer Contact

For security issues or sensitive matters, contact maintainers directly:
- Security issues: See [SECURITY.md](SECURITY.md)
- Other private matters: Open an issue and tag maintainers

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project documentation

Thank you for contributing to LionAGI QE Fleet!

---

**Questions?** Open a discussion or issue - we're here to help!
