import sys
import re
from .calculator import Calculator

def main():
    if len(sys.argv) != 2:
        print("Usage: ccli \"<number1> <operator> <number2>\"")
        print("Example: ccli \"1 + 2\"")
        sys.exit(1)

    expr = sys.argv[1].strip()
    match = re.match(r'^\s*(\d*\.?\d+)\s*([+\-*/])\s*(\d*\.?\d+)\s*$', expr)
    if not match:
        print(f"Error: Invalid expression format. Expected '<number> <operator> <number>', you entered: {expr}")
        print("Example: ccli \"3 + 2\" or ccli \"10.5 * 2\"")
        sys.exit(1)

    a_str, op, b_str = match.groups()
    calc = Calculator()

    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        print("Error: Numbers must be valid numeric values")
        sys.exit(1)

    operations = {
        '+': calc.add,
        '-': calc.subtract,
        '*': calc.multiply,
        '/': calc.divide
    }

    if op not in operations:
        print("Error: Operator must be one of +, -, *, /")
        sys.exit(1)

    try:
        result = operations[op](a, b)
        print(f"Result: {result}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()