# shs_calculator

这是一个简单的计算器项目示例，包含了最基本的 **加减乘除** 函数，并提供了命令行 `ccli`命令行工具，完美演示了Python包的应用过程，适合初学者参考。


<br/>


> 📌 更多学习内容，请参考 [**Python项目全流程指南**](https://github.com/hollson/shs_calculator/blob/master/docs/Python%E9%A1%B9%E7%9B%AE%E5%85%A8%E6%B5%81%E7%A8%8B%E6%8C%87%E5%8D%97.md)  



<br/>



## 🚀 安装方法

要求 Python 3.12 及以上版本，通过 pip 快速安装：

```bash
pip install shs_calculator
```



<br/>



## 📚 使用示例

### 基本用法

```python
from shs_calculator import Calculator

# 创建计算器实例
calc = Calculator()

# 执行基础算术运算
print(calc.add(2, 3))       # 输出：5
print(calc.subtract(10, 4)) # 输出：6
print(calc.multiply(5, 6))  # 输出：30
print(calc.divide(8, 2))    # 输出：4.0

# 处理除零异常（会抛出 ValueError）
try:
    calc.divide(5, 0)
except ValueError as e:
    print(e)  # 输出：不允许除以零
```



### 命令行用法

shs_calculator默认提供了`ccli`命令行工具，使用方式如下： 

```bash
ccli "1 + 2"
ccli "3 - 1"
ccli "2 * 3"
ccli "8 / 2"
```



<br/>



## 📜 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件。



<br/>



## 📞 支持与反馈

如果有任何问题或建议，欢迎在 [GitHub](https://github.com/hollson/shs_calculator/issues) 上提交 Issue。