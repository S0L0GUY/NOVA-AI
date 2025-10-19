# Quick Start - Code Quality Checks

This is a quick reference guide for developers working with NOVA-AI's code quality checks.

## Before Committing Your Code

Run these commands to check your code locally:

```bash
# Install all quality check tools
pip install flake8 black isort

# Auto-fix formatting issues
black .
isort .

# Check for code issues
flake8 .
```

## Common Workflows

### Fix All Formatting Issues
```bash
# This will automatically format your code
black .
isort .
```

### Check Code Quality
```bash
# Check for syntax errors and critical issues
flake8 . --select=E9,F63,F7,F82

# Check import sorting
isort --check-only .

# Check code formatting
black --check .
```

### Before Creating a Pull Request

1. **Format your code:**
   ```bash
   black .
   isort .
   ```

2. **Check for issues:**
   ```bash
   flake8 .
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

4. **The automated checks will run automatically** on your pull request

## What Happens When You Push?

All these checks run automatically:
- ✓ **Flake8** - Finds code style and syntax issues
- ✓ **Black** - Checks code formatting
- ✓ **isort** - Checks import ordering
- ✓ **Pylint** - Advanced code analysis
- ✓ **MyPy** - Type checking
- ✓ **Coverage** - Test coverage
- ✓ **pip-audit** - Security scanning
- ✓ **Requirements** - Validates dependencies
- ✓ **Pydocstyle** - Docstring checking
- ✓ **Sphinx** - Documentation build

## Fixing Failed Checks

### Black or isort Failed?
```bash
# Auto-fix these issues
black .
isort .
git add .
git commit -m "Fix formatting"
git push
```

### Flake8 Failed?
Read the error messages and fix manually. Common issues:
- Unused imports
- Undefined variables
- Syntax errors
- Lines too long (max 127 chars)

### Pylint or MyPy Issues?
These are usually warnings and won't block your PR. Fix them if possible, but don't worry if they're too complex.

## Installing Tools Locally

```bash
# Minimal setup (recommended)
pip install black isort flake8

# Full setup (all tools)
pip install flake8 pylint black isort mypy coverage pytest pip-audit pydocstyle sphinx
```

## Quick Tips

- ⚡ **Always run `black .` and `isort .` before committing** - these auto-fix most issues
- 📝 **Flake8 errors are usually easy to fix** - read the error message carefully
- 🔍 **Pylint and MyPy warnings** are informational - fix if you can, but they won't block PRs
- 🔒 **pip-audit security warnings** should be addressed by updating packages
- 📚 **Add docstrings** to public functions and classes

## Need Help?

- See [CODE_QUALITY.md](CODE_QUALITY.md) for detailed documentation
- Check workflow files in `.github/workflows/` for configuration
- Check configuration files: `.flake8`, `.pylintrc`, `pyproject.toml`

## Bypassing Checks (Emergency Only)

If you absolutely need to bypass checks temporarily (not recommended):
- Add `[skip ci]` to your commit message to skip ALL checks
- This should only be used for documentation-only changes or emergencies

**Better approach**: Fix the issues or ask for help!
