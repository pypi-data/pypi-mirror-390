"""
连续数相加实现
处理两个连续整数的加法，如49+50=99
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ConsecutiveNumberAddition(MathCalculator):
    """连续数相加算法"""
    
    def __init__(self):
        super().__init__("连续数相加", "两个连续整数的相加", priority=8)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个连续的整数相加"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, int) and isinstance(addend2, int)):
                return False
            
            # 检查是否为连续数（差值为1）
            return abs(addend1 - addend2) == 1
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建连续数相加步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        # 确保第一个数是较小的
        if addend1 > addend2:
            addend1, addend2 = addend2, addend1
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 识别连续数相加",
            operation="识别连续数",
            result=f"{addend1}和{addend2}是连续整数"
        ))
        
        steps.append(CalculationStep(
            description=f"连续整数相加 = 2n + 1",
            operation="应用连续数相加规律",
            result=f"n = {addend1}, 2n + 1 = {2 * addend1 + 1}"
        ))
        
        result = addend1 + addend2
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} = {result}",
            operation="计算结果",
            result=result,
            formula="n + (n+1) = 2n + 1"
        ))
        
        return steps