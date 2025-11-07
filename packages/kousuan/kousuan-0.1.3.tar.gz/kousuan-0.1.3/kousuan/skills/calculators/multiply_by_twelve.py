"""
乘以12实现
乘以12，等于原数乘以10再加上原数的2倍
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByTwelve(MathCalculator):
    """乘以12算法"""
    
    def __init__(self):
        super().__init__("乘12速算", "乘以12等于乘10再加2倍", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数乘以12"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 检查是否有一个数是12
            return a == 12 or b == 12
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘12速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是12，哪个是被乘数
        if a == 12:
            multiplied_num = b
        else:
            multiplied_num = a
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 12 使用乘12速算法",
            operation="识别模式",
            result="12 = 10 + 2，转换为乘10加2倍"
        ))
        
        # 计算乘以10
        times_ten = multiplied_num * 10
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 10 = {times_ten}",
            operation="乘以10",
            result=times_ten
        ))
        
        # 计算2倍
        times_two = multiplied_num * 2
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 2 = {times_two}",
            operation="计算2倍",
            result=times_two
        ))
        
        # 相加得到最终结果
        final_result = times_ten + times_two
        steps.append(CalculationStep(
            description=f"{times_ten} + {times_two} = {final_result}",
            operation="相加得结果",
            result=final_result,
            formula="a × 12 = a × 10 + a × 2"
        ))
        
        return steps