import unittest
from shs_calculator import Calculator

class TestCalculator(unittest.TestCase):
    """Calculator 类的单元测试用例"""

    def setUp(self):
        """每个测试方法执行前初始化计算器实例"""
        self.calc = Calculator()

    def test_add(self):
        """测试加法运算"""
        # 整数加法
        self.assertEqual(self.calc.add(2, 3), 5)
        # 负数加法
        self.assertEqual(self.calc.add(-1, 1), 0)
        # 浮点数加法
        self.assertEqual(self.calc.add(3.5, 2.5), 6.0)
        # 零值加法
        self.assertEqual(self.calc.add(0, 0), 0)

    def test_subtract(self):
        """测试减法运算"""
        self.assertEqual(self.calc.subtract(10, 4), 6)
        self.assertEqual(self.calc.subtract(5, 8), -3)
        self.assertEqual(self.calc.subtract(7.2, 2.2), 5.0)
        self.assertEqual(self.calc.subtract(0, 5), -5)

    def test_multiply(self):
        """测试乘法运算"""
        self.assertEqual(self.calc.multiply(5, 6), 30)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(2.5, 4), 10.0)
        self.assertEqual(self.calc.multiply(0, 100), 0)

    def test_divide(self):
        """测试除法运算"""
        self.assertEqual(self.calc.divide(8, 2), 4.0)
        self.assertEqual(self.calc.divide(-9, 3), -3.0)
        self.assertEqual(self.calc.divide(5, 2), 2.5)
        # 浮点数除数
        self.assertAlmostEqual(self.calc.divide(1, 3), 0.3333333333333333)

    def test_divide_by_zero(self):
        """测试除零异常"""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(5, 0)
        self.assertEqual(str(context.exception), "除数不能为零")

if __name__ == "__main__":
    # 运行所有测试用例
    unittest.main()