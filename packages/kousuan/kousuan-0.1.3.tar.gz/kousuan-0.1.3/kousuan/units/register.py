"""
单位换算算子注册器
"""

from .calculators import (
    LengthUnitCalculator,
    TimeUnitCalculator,
    MassUnitCalculator,
    CurrencyUnitCalculator,
    NumberUnitCalculator,
    PercentageDiscountCalculator,
    PercentageCalculator,
    DiscountCalculator,
    AreaUnitCalculator,
    VolumeUnitCalculator,
)

class UnitCalculatorRegister:
    """单位换算算子注册器"""
    
    def __init__(self):
        self.calculators = []
        self._register_default_calculators()
    
    def _register_default_calculators(self):
        """注册默认的单位换算算子"""
        self.register(LengthUnitCalculator())
        self.register(NumberUnitCalculator())
        self.register(PercentageCalculator())
        self.register(DiscountCalculator())
        self.register(PercentageDiscountCalculator())  # 通用的放在最后
        self.register(TimeUnitCalculator())
        self.register(MassUnitCalculator())
        self.register(CurrencyUnitCalculator())
        self.register(AreaUnitCalculator())
        self.register(VolumeUnitCalculator())

    def register(self, calculator):
        """注册新的单位换算算子"""
        self.calculators.append(calculator)
    
    def clear(self):
        """清空注册的算子"""
        self.calculators = []
    
    def get_calculators(self):
        """获取所有注册的算子"""
        return self.calculators
    
    def find_calculator(self, problem):
        """查找匹配的算子"""
        for calculator in self.calculators:
            if calculator.is_match_pattern(problem):
                return calculator
        return None
    
    def calculate(self, problem):
        """计算接口"""
        calculator = self.find_calculator(problem)
        if calculator is not None:
            return calculator.solve(problem)
        else:
            raise ValueError("没有找到匹配的单位换算算子")