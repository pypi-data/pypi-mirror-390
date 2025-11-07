"""
破十法实现
20以内退位减法，将被减数拆分成10和剩余部分
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class BreakTenSubtraction(MathCalculator):
    """破十法（20以内退位减法）"""
    
    def __init__(self):
        super().__init__("破十法", "20以内退位减法，将被减数拆分成10和剩余部分", priority=2)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：20以内的退位减法"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            # 20以内的整数，且需要退位（被减数个位小于减数）
            return (isinstance(a, int) and isinstance(b, int) and 
                   10 <= a <= 20 and 0 < b <= 10 and a % 10 < b)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建破十法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 拆分被减数
        tens = (a // 10) * 10
        ones = a % 10
        
        steps = [
            CalculationStep(
                description=f"将 {a} 拆分为 {tens} 和 {ones}",
                operation=f"拆分被减数",
                result=f"{a} = {tens} + {ones}"
            ),
            CalculationStep(
                description=f"先算 {tens} - {b} = {tens - b}",
                operation=f"用整十数减",
                result=tens - b
            ),
            CalculationStep(
                description=f"再算 {tens - b} + {ones} = {tens - b + ones}",
                operation=f"加上个位数",
                result=tens - b + ones
            )
        ]
        
        return steps