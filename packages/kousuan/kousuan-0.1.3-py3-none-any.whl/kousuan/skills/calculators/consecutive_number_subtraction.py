"""
连续数减法实现
处理两个连续整数的减法，结果恒为1
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ConsecutiveNumberSubtraction(MathCalculator):
    """连续数减法算法"""
    
    def __init__(self):
        super().__init__("连续数减法", "两个连续整数的减法，结果恒为1", priority=7)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个连续的整数相减"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 检查是否为连续数（差值为1）
            return (minuend - subtrahend == 1)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建连续数减法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 识别连续数减法",
            operation="识别连续数",
            result=f"{minuend}和{subtrahend}是连续整数"
        ))
        
        steps.append(CalculationStep(
            description=f"连续整数相减的差值恒为1",
            operation="应用连续数减法规律",
            result="前数减后数 = 1"
        ))
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} = 1",
            operation="得出结果",
            result=1,
            formula="(n+1) - n = 1"
        ))
        
        return steps