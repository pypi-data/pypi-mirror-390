# shs_calculator

A simple Python calculator project example that fully demonstrates the entire workflow from project creation, coding, testing, packaging to publishing on PyPI. It's perfect for beginners learning Python project development and distribution.

> 📌 中文文档：[README.zh.md](README.zh.md)



## 🌟 Core Features

- Supports basic arithmetic operations: addition, subtraction, multiplication, division
- Clear project structure for easy reference by beginners
- Full workflow demonstration (coding → testing → packaging → publishing)
- Simple installation and convenient usage
- Well-commented code suitable for learning
- Includes exception handling (e.g., division by zero)



## 📋 Project Structure

```bash
shs_calculator/
├── shs_calculator/          # Main package directory
│   ├── __init__.py         # Package initialization file
│   ├── cli.py              # Command line interface (optional)
│   └── calculator.py        # Core calculator logic (implementation code below)
├── tests/                   # Test directory
│   ├── __init__.py
│   └── test_calculator.py   # Unit test file (using unittest)
├── pyproject.toml           # Packaging configuration file (compliant with PEP 621)
├── README.md                # Project documentation (this file)
└── LICENSE                  # License file (MIT recommended)
```



## 🚀 Installation

Requires Python 3.12 or higher. Install quickly via pip:

```bash
pip install shs_calculator
```



## 🧪 Running Tests

```shell
# Method 1: Run the test file directly
python -m tests.test_calculator

# Method 2: Use unittest to discover all test cases
python -m unittest discover -s tests -v

```



## 📖 Usage Examples

### Basic Usage

```python
from shs_calculator import Calculator

# Create calculator instance
calc = Calculator()

# Perform basic arithmetic operations
print(calc.add(2, 3))       # Output: 5
print(calc.subtract(10, 4)) # Output: 6
print(calc.multiply(5, 6))  # Output: 30
print(calc.divide(8, 2))    # Output: 4.0

# Handle division by zero exception (raises ValueError)
try:
    calc.divide(5, 0)
except ValueError as e:
    print(e)  # Output: Division by zero is not allowed
```

### Command Line Usage (Optional)

If you added a CLI entry point, you can use it directly in the terminal:

```bash
# Example CLI usage (adjust based on your actual implementation)
shs-calc "2 + 3"
shs-calc "10 - 4"
shs-calc "5 * 6"
shs-calc "8 / 2"
```



## 📚 Learning Content

Designed specifically for beginners, you can learn:
- How to structure a Python project properly
- Writing clear, commented, and testable core code
- Implementing basic exception handling logic
- Writing unit tests with Python's built-in `unittest` framework
- Packaging projects with `setuptools` and `pyproject.toml` (compliant with PEP 621)
- The complete process of publishing projects to PyPI
- Writing concise and practical project documentation



## 📜 License

This project is open-source under the MIT License - see the [LICENSE](LICENSE) file for details.



## 📞 Support & Feedback

If you have any questions or suggestions, feel free to submit an Issue on [GitHub](https://github.com/hollson/shs_calculator).