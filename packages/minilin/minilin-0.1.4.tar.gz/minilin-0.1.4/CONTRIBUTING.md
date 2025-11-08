# Contributing to MiniLin

Thank you for your interest in contributing to MiniLin! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

We love feature suggestions! Please open an issue with:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/minilin-ai/minilin.git
   cd minilin
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PEP 8 style guide
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone repository
git clone https://github.com/minilin-ai/minilin.git
cd minilin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,all]"

# Run tests
pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for all public functions
- Keep functions focused and small

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## Documentation

- Update README.md if adding new features
- Add docstrings to all public APIs
- Include examples for new functionality

## Questions?

Feel free to open an issue or reach out to contact@minilin.ai

Thank you for contributing! 🎉
