# Contributing to NOVA-AI

Thank you for considering contributing to NOVA-AI! We welcome contributions from everyone.

## How to Contribute

1. **Fork the repository**: Click the "Fork" button at the top right of this page.
2. **Clone your fork**: Clone your fork to your local machine using `git clone https://github.com/YOUR-USERNAME/NOVA-AI.git`.
3. **Create a branch**: Create a new branch for your work using `git checkout -b your-branch-name`.
4. **Make your changes**: Make your changes to the codebase.
5. **Commit your changes**: Commit your changes with a descriptive commit message using `git commit -m "Description of changes"`.
6. **Push to your fork**: Push your changes to your fork using `git push origin your-branch-name`.
7. **Open a Pull Request**: Open a pull request on the original repository.

## Pull Request Guidelines

- Ensure your code follows the existing style of the project.
- Write clear, concise commit messages.
- Include any relevant documentation updates.
- Be responsive to feedback during the review process.

## Running Tests & Linting

- **Quick smoke test:** Run `python smoke_test.py` to verify core components.
- **Unit/Integration tests:** Add tests under a `tests/` folder and run your
	test runner of choice. (This repo currently provides a smoke test as a
	quick sanity check.)
- **Linting:** Run `flake8` (or your configured linter/formatter) before
	opening a PR.

## PR Checklist

- **Update documentation:** Ensure relevant docs (`README.md`, `CONTRIBUTING.md`,
	or `prompts/` docs) are updated for your change.
- **Run smoke test:** Execute `python smoke_test.py` and include any failures
	or observations in your PR description.
- **Run linter/formatting:** Confirm `flake8` and formatting tools pass locally.
- **Descriptive PR:** Include a brief description of the change, motivation,
	and any special runtime steps required.

Thank you for your contributions!
