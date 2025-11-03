# Code Quality Checks

This document describes the automated code quality checks that run on every pull request, push, and merge in the NOVA-AI repository.

## Available Checks

### 1. Flake8 - Python Linting
**Workflow**: `.github/workflows/flake8.yml`  
**Configuration**: `.flake8`

Flake8 checks for Python code style issues and potential errors:
- Syntax errors and undefined names (blocking)
- Code style violations (warnings)
- Code complexity analysis
- Maximum line length: 127 characters

**Run locally**:
```bash
pip install flake8
flake8 .
```

### 2. Pylint - Advanced Code Analysis
**Workflow**: `.github/workflows/pylint.yml`  
**Configuration**: `.pylintrc`

Pylint performs comprehensive static code analysis:
- Code structure and organization
- Potential bugs and errors
- Code quality metrics
- Best practice violations

**Run locally**:
```bash
pip install pylint
pylint $(find . -name "*.py" -not -path "./.git/*" -not -path "./__pycache__/*")
```

### 3. Black - Code Formatting
**Workflow**: `.github/workflows/black.yml`  
**Configuration**: `pyproject.toml`

Black ensures consistent code formatting:
- Automatically formats Python code
- Line length: 127 characters
- Consistent style across the codebase

**Run locally**:
```bash
pip install black
black --check .  # Check without modifying
black .          # Format all files
```

### 4. isort - Import Sorting
**Workflow**: `.github/workflows/isort.yml`  
**Configuration**: `pyproject.toml`

isort organizes and sorts Python imports:
- Groups imports by type (standard library, third-party, local)
- Alphabetical sorting within groups
- Compatible with Black formatter

**Run locally**:
```bash
pip install isort
isort --check-only .  # Check without modifying
isort .               # Sort all imports
```

### 5. MyPy - Type Checking
**Workflow**: `.github/workflows/mypy.yml`  
**Configuration**: `pyproject.toml`

MyPy performs static type checking:
- Validates type hints
- Catches type-related bugs
- Improves code documentation

**Run locally**:
```bash
pip install mypy
mypy .
```

### 6. Coverage.py - Test Coverage
**Workflow**: `.github/workflows/coverage.yml`  
**Configuration**: `pyproject.toml`

Coverage.py measures test coverage:
- Tracks which code is executed by tests
- Generates coverage reports
- Helps identify untested code

**Run locally**:
```bash
pip install coverage pytest
coverage run -m pytest
coverage report
coverage html  # Generate HTML report
```

### 7. pip-audit - Security Scanning
**Workflow**: `.github/workflows/pip-audit.yml`

pip-audit scans for known security vulnerabilities:
- Checks all dependencies in requirements.txt
- Reports known CVEs
- Suggests package updates
- Runs weekly on schedule

**Run locally**:
```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### 8. Requirements Consistency Check
**Workflow**: `.github/workflows/requirements-check.yml`

Validates requirements.txt file:
- Checks file exists and is valid
- Detects duplicate packages
- Validates package installation
- Ensures consistency

**Run locally**:
```bash
pip install --dry-run -r requirements.txt
```

### 9. Pydocstyle - Docstring Style
**Workflow**: `.github/workflows/pydocstyle.yml`  
**Configuration**: `pyproject.toml`

Pydocstyle checks Python docstring conventions:
- Validates docstring format
- Ensures documentation completeness
- Follows Google style convention

**Run locally**:
```bash
pip install pydocstyle
pydocstyle .
```

### 10. Sphinx - Documentation Build
**Workflow**: `.github/workflows/sphinx.yml`

Sphinx builds documentation:
- Auto-generates API documentation
- Creates HTML documentation
- Validates documentation builds correctly
- Uploads build artifacts

**Run locally**:
```bash
pip install sphinx sphinx-rtd-theme
cd docs
make html
```

## When Checks Run

All checks run automatically on:
- **Push** to main, master, dev, or develop branches
- **Pull Requests** targeting main, master, dev, or develop branches
- **Merge Groups** (when merging PRs)

Additionally:
- **pip-audit** runs weekly on Monday at 9:00 AM UTC

## Passing Criteria

### Blocking Checks (must pass):
- Flake8 syntax errors (E9, F63, F7, F82)
- Black code formatting
- isort import sorting
- Requirements consistency

### Warning Checks (informational):
- Flake8 style warnings
- Pylint issues
- MyPy type errors
- Pydocstyle violations
- Coverage reports
- pip-audit vulnerabilities (informational)

## Configuration Files

- **`.flake8`** - Flake8 configuration
- **`.pylintrc`** - Pylint configuration
- **`pyproject.toml`** - Configuration for Black, isort, MyPy, Coverage, and Pydocstyle
- **`.gitignore`** - Updated to exclude check outputs

## Running All Checks Locally

To run all checks before pushing:

```bash
# Install all tools
pip install flake8 pylint black isort mypy coverage pytest pip-audit pydocstyle

# Run checks
flake8 .
pylint $(find . -name "*.py" -not -path "./.git/*")
black --check .
isort --check-only .
mypy .
pydocstyle .
pip-audit -r requirements.txt

# Run tests with coverage
coverage run -m pytest
coverage report
```

## Fixing Issues

### Auto-fix formatting:
```bash
black .
isort .
```

### Fix specific issues:
- **Flake8/Pylint**: Review output and fix manually
- **MyPy**: Add type hints or adjust configuration
- **Pydocstyle**: Add or fix docstrings
- **pip-audit**: Update vulnerable packages

## CI/CD Integration

All workflows are configured to:
- Use Python 3.11 (configurable)
- Install project dependencies when needed
- Generate actionable reports
- Upload artifacts (documentation)
- Provide clear pass/fail status

## Maintenance

### Updating configurations:
1. Edit the configuration files (`.flake8`, `.pylintrc`, `pyproject.toml`)
2. Test changes locally
3. Commit and push changes
4. Workflows will use updated configurations automatically

### Disabling specific checks:
- Remove or comment out workflow files in `.github/workflows/`
- Or modify workflow triggers to exclude certain branches

## Best Practices

1. **Run checks locally** before pushing code
2. **Fix Black and isort issues** first (they're auto-fixable)
3. **Address Flake8 errors** before style warnings
4. **Use type hints** to help MyPy
5. **Write docstrings** for public functions and classes
6. **Keep dependencies updated** to address security issues
7. **Write tests** to improve coverage

## Getting Help

If you encounter issues with any check:
1. Read the check's output carefully
2. Check the configuration files
3. Run the check locally to debug
4. Consult the tool's documentation:
   - [Flake8](https://flake8.pycqa.org/)
   - [Pylint](https://pylint.org/)
   - [Black](https://black.readthedocs.io/)
   - [isort](https://pycqa.github.io/isort/)
   - [MyPy](https://mypy.readthedocs.io/)
   - [Coverage.py](https://coverage.readthedocs.io/)
   - [pip-audit](https://github.com/pypa/pip-audit)
   - [Pydocstyle](https://www.pydocstyle.org/)
   - [Sphinx](https://www.sphinx-doc.org/)
