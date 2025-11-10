class Calculator:
    """简单的计算器类"""

    def add(self, a, b):
        """加法"""
        return a + b

    def subtract(self, a, b):
        """减法"""
        return a - b

    def multiply(self, a, b):
        """乘法"""
        return a * b

    def divide(self, a, b):
        """除法"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b

    def run_demo(self):
        """运行演示"""
        print("=== 简单计算器演示 ===")
        print(f"5 + 3 = {self.add(5, 3)}")
        print(f"10 - 4 = {self.subtract(10, 4)}")
        print(f"6 * 7 = {self.multiply(6, 7)}")
        print(f"15 / 3 = {self.divide(15, 3)}")