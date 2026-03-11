# Contributing to Polymarket Arbitrage Bot

Thank you for your interest in contributing to the Frank-Wolfe Arbitrage Algorithm project! We welcome contributions from the community.

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

---

## 🚀 Getting Started

### Fork the Repository

1. Go to the [repository](https://github.com/KJjjj0/polymarket-arbitrage)
2. Click the "Fork" button in the top-right corner
3. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/polymarket-arbitrage.git
   cd polymarket-arbitrage
   ```

### Create a Branch

Create a new branch for your feature or bug fix:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## 🔧 Development Setup

### Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
python3 test.py

# Run examples
python3 examples/basic_arb.py
python3 examples/visualization.py
```

---

## 📝 Contribution Guidelines

### Types of Contributions

We welcome the following types of contributions:

1. **Bug Fixes**: Fix any issues or errors you find
2. **New Features**: Add new algorithms, strategies, or tools
3. **Documentation**: Improve or add documentation
4. **Examples**: Add new usage examples
5. **Performance**: Improve code performance
6. **Testing**: Add or improve tests

### Before Contributing

1. Check existing [Issues](https://github.com/KJjjj0/polymarket-arbitrage/issues) to avoid duplicates
2. Discuss significant changes in an issue first
3. Ensure your code follows our style guidelines

---

## 🎨 Code Style

### Python Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Add comments for complex logic

### Comment Language

- Use **Chinese** for comments in existing Chinese files
- Use **English** for comments in new English files
- Keep consistency with the file's original language

### Example

```python
def calculate_arbitrage_profit(markets: List[Dict]) -> float:
    """
    Calculate arbitrage profit from given markets.

    Args:
        markets: List of market data

    Returns:
        Arbitrage profit
    """
    # 计算总利润
    total_profit = 0.0

    for market in markets:
        profit = market['price_yes'] + market['price_no']
        if profit < 1.0:
            total_profit += (1.0 - profit)

    return total_profit
```

---

## 📤 Submitting Changes

### Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Fix: Add error handling for invalid market prices"
```

### Commit Message Format

Use conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

### Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
```

### Pull Request Checklist

Before submitting a PR, ensure:
- [ ] Code passes all tests
- [ ] Code follows style guidelines
- [ ] Documentation is updated (if needed)
- [ ] Commit messages are clear
- [ ] PR description explains the changes

---

## 🐛 Reporting Issues

### When Reporting Issues

Include the following information:

1. **Python Version**: e.g., 3.10.0
2. **Operating System**: e.g., Ubuntu 22.04
3. **Steps to Reproduce**: Detailed steps
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Error Messages**: Full error traceback

### Issue Template

```markdown
**Description**
A brief description of the issue.

**Steps to Reproduce**
1. Step 1
2. Step 2
3. ...

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- Python Version: 3.10.0
- OS: Ubuntu 22.04
- Dependencies: list versions if relevant

**Additional Context**
Any other context about the issue.
```

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 💬 Questions or Need Help?

- Open an [Issue](https://github.com/KJjjj0/polymarket-arbitrage/issues)
- Check existing [Discussions](https://github.com/KJjjj0/polymarket-arbitrage/discussions)
- Contact maintainers

---

## 🙏 Acknowledgments

Thank you for your contributions! Your help makes this project better for everyone.

---

<div align="center">

**Happy Coding! 🚀**

Made with ❤️ by Polymarket Arbitrage Bot

</div>
