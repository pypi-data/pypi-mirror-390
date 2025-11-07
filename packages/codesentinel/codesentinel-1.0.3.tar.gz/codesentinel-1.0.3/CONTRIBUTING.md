# Contributing to CodeSentinel

Thank you for your interest in contributing to CodeSentinel! This document provides guidelines and information for contributors.

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/joediggidyyy/CodeSentinel.git
   cd CodeSentinel
   ```

2. **Set up development environment:**

   ```bash
   # Install development dependencies
   pip install -r requirements.txt
   pip install pytest black mypy build twine

   # Optional: Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Run tests:**

   ```bash
   python run_tests.py
   ```

## Development Workflow

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**

   ```bash
   # Format code
   black codesentinel tests

   # Type check
   mypy codesentinel --ignore-missing-imports

   # Run tests
   python run_tests.py
   ```

4. **Commit your changes:**

   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push and create a pull request:**

   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- **Formatting:** We use Black for code formatting
- **Type hints:** Use type hints where possible
- **Docstrings:** Use Google-style docstrings
- **Imports:** Group imports (standard library, third-party, local)

## Testing

- Write unit tests for new functionality
- Aim for good test coverage
- Run the full test suite before submitting PRs

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update this CONTRIBUTING.md if development processes change

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Request review from maintainers
4. Address review feedback
5. Merge when approved

## Reporting Issues

- Use GitHub Issues to report bugs
- Provide detailed reproduction steps
- Include relevant system information
- Suggest fixes if possible

## License

By contributing to CodeSentinel, you agree that your contributions will be licensed under the MIT License.

