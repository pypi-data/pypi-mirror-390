"""
同数相加实现
处理两个相同数字的加法，直接翻倍
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SameNumberAddition(MathCalculator):
    """同数相加算法"""
    
    def __init__(self):
        super().__init__("同数相加", "两个相同数字的加法，直接翻倍", priority=9)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个相同的数字相加"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, int) and isinstance(addend2, int)):
                return False
            
            # 两个数必须完全相等
            return addend1 == addend2
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建同数相加步骤"""
        numbers = formula.get_numbers()
        addend = int(numbers[0].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend} + {addend} 识别同数相加",
            operation="识别同数",
            result="两个相同的数相加"
        ))
        
        steps.append(CalculationStep(
            description=f"同数相加等于该数的2倍",
            operation="应用同数相加规律",
            result="直接翻倍计算"
        ))
        
        result = addend * 2
        steps.append(CalculationStep(
            description=f"{addend} + {addend} = 2 × {addend} = {result}",
            operation="计算结果",
            result=result,
            formula="a + a = 2a"
        ))
        
        return steps