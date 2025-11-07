"""
同数相减实现
处理两个相同数字的减法，结果恒为0
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SameNumberSubtraction(MathCalculator):
    """同数相减算法"""
    
    def __init__(self):
        super().__init__("同数相减", "两个相同数字的减法，结果恒为0", priority=8)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个相同的数字相减"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 两个数必须完全相等
            return minuend == subtrahend
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建同数相减步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 识别同数相减",
            operation="识别同数",
            result="两个相同的数相减"
        ))
        
        steps.append(CalculationStep(
            description=f"任何数减去自身都等于0",
            operation="应用同数相减规律",
            result="结果恒为0"
        ))
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} = 0",
            operation="得出结果",
            result=0,
            formula="a - a = 0"
        ))
        
        return steps