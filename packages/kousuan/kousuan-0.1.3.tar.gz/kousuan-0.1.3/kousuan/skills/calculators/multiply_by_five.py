"""
乘5速算法实现
任何数乘5，先乘10再除以2
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByFive(MathCalculator):
    """乘5速算法"""
    
    def __init__(self):
        super().__init__("乘5速算", "任何数乘5，先乘10再除以2", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任何数乘以5"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            return (a == 5 and isinstance(b, (int, float))) or (b == 5 and isinstance(a, (int, float)))
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘5步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是5
        if a == 5:
            num = b
        else:
            num = a
        
        # 计算
        step1_result = num * 10
        final_result = step1_result / 2
        
        steps = [
            CalculationStep(
                description=f"{num} × 5 使用乘5速算法",
                operation="识别模式",
                result="使用先乘10再除以2的方法"
            ),
            CalculationStep(
                description=f"{num} × 10 = {step1_result}",
                operation="乘以10",
                result=step1_result
            ),
            CalculationStep(
                description=f"{step1_result} ÷ 2 = {final_result}",
                operation="除以2", 
                result=int(final_result) if final_result.is_integer() else final_result,
                formula="数×5 = (数×10)÷2"
            )
        ]
        
        return steps