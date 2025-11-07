"""
乘以15实现
乘以15，等于原数加它的一半，再乘以10
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByFifteen(MathCalculator):
    """乘以15算法"""
    
    def __init__(self):
        super().__init__("乘15速算", "乘以15等于原数加一半再乘10", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数乘以15"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 检查是否有一个数是15
            return a == 15 or b == 15
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘15速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是15，哪个是被乘数
        if a == 15:
            multiplied_num = b
        else:
            multiplied_num = a
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 15 使用乘15速算法",
            operation="识别模式",
            result="15 = 10 + 5，利用15 = 1.5 × 10的特点"
        ))
        
        # 计算一半
        half_value = multiplied_num / 2
        steps.append(CalculationStep(
            description=f"{multiplied_num} ÷ 2 = {half_value}",
            operation="计算一半",
            result=half_value
        ))
        
        # 原数加一半
        sum_value = multiplied_num + half_value
        steps.append(CalculationStep(
            description=f"{multiplied_num} + {half_value} = {sum_value}",
            operation="原数加一半",
            result=sum_value
        ))
        
        # 乘以10得到最终结果
        final_result = sum_value * 10
        if final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"{sum_value} × 10 = {final_result}",
            operation="乘以10",
            result=final_result,
            formula="a × 15 = (a + a÷2) × 10"
        ))
        
        return steps