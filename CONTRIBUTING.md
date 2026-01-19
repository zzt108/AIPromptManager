# Contributing to AIPromptManager

Thank you for considering contributing to AIPromptManager! 🎉

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what is best for the community

## How to Contribute

### Reporting Bugs

- Use the GitHub issue tracker
- Include Python version, OS, and steps to reproduce
- Provide error messages and logs if applicable

### Suggesting Features

- Open an issue with `[Feature Request]` prefix
- Describe the use case and expected behavior
- Explain why this would be useful

### Code Contributions

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AIPromptManager.git
cd AIPromptManager

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install in development mode
pip install -e ".[dev]"
```

#### Code Standards

- **Python 3.10+** required
- **Type hints**: All functions must have type annotations
- **Formatting**: Use `black` (line length 88)
- **Type checking**: Code must pass `mypy --strict`
- **Testing**: All new features require tests

#### Before Submitting

Run these checks:

```bash
# Run tests
pytest tests/ -v

# Type check
mypy --strict src/

# Format code
black src/ tests/
```

#### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and type checking
5. Commit with clear messages (`git commit -m "Add amazing feature"`)
6. Push to your fork
7. Open a Pull Request

#### Commit Messages

Follow conventional commits:
- `feat: Add new feature`
- `fix: Fix bug in registry service`
- `docs: Update README`
- `test: Add tests for config panel`
- `refactor: Simplify main window logic`

### Testing

- Write tests for all new functionality
- Ensure existing tests still pass
- Aim for high coverage

### Documentation

- Update README.md for user-facing changes
- Update .doc/README-AIPromptManager.md for detailed docs
- Add docstrings to all public functions/classes

## Questions?

Open an issue with `[Question]` prefix or start a discussion on GitHub.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
