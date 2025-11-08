# Contributing to numgraph

Thank you for your interest in contributing to numgraph! 🎉

## Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/numgraph.git
   cd numgraph
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write tests** for your changes in the `tests/` directory

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and create a Pull Request**

## Coding Standards

- Follow PEP 8 style guidelines
- Write docstrings for all functions and classes
- Add type hints where appropriate
- Keep functions focused and concise
- Write meaningful commit messages

## Testing

- All new features must include tests
- Aim for high test coverage
- Run tests before submitting PR:
  ```bash
  pytest tests/ -v --cov=numgraph
  ```

## Documentation

- Update README.md if adding new features
- Add docstrings to new functions/classes
- Include examples for new functionality

## Commit Message Format

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding tests
- `refactor:` - Code refactoring

## Questions?

Feel free to open an issue for discussion!

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.
