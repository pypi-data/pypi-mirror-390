import sys
import re
from .calculator import Calculator

def main():
    if len(sys.argv) != 2:
        print("用法: shs-calc \"<数字1> <运算符> <数字2>\"")
        print("示例: shs-calc \"1 + 2\"")
        sys.exit(1)

    expr = sys.argv[1].strip()

    # 简单的正则匹配：匹配如 "3 + 5" 这种格式
    match = re.match(r'^\s*(\d*\.?\d+)\s*([+\-*/])\s*(\d*\.?\d+)\s*$', expr)
    if not match:
        print(f"错误：表达式格式不正确，应为 '<数字> <运算符> <数字>'，您输入的是：{expr}")
        print("示例：shs-calc \"3 + 2\" 或 shs-calc \"10.5 * 2\"")
        sys.exit(1)

    a_str, op, b_str = match.groups()
    calc = Calculator()

    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        print("错误：数字必须为有效数值")
        sys.exit(1)

    operations = {
        '+': calc.add,
        '-': calc.subtract,
        '*': calc.multiply,
        '/': calc.divide
    }

    if op not in operations:
        print("错误：运算符必须是 +, -, *, / 之一")
        sys.exit(1)

    try:
        result = operations[op](a, b)
        print(f"结果: {result}")
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()