"""
同头数减法实现
处理十位相同的两位数减法，如74-42=32
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SameHeadSubtraction(MathCalculator):
    """同头数减法算法"""
    
    def __init__(self):
        super().__init__("同头数减法", "十位相同的两位数减法", priority=8)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：十位相同的两位数减法"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 两位数且十位相同，个位能够减
            if not (10 <= minuend <= 99 and 10 <= subtrahend <= 99):
                return False
            
            minuend_tens = minuend // 10
            subtrahend_tens = subtrahend // 10
            minuend_ones = minuend % 10
            subtrahend_ones = subtrahend % 10
            
            # 十位相同且个位能够减（不需要借位）
            return (minuend_tens == subtrahend_tens and minuend_ones >= subtrahend_ones)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建同头数减法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        minuend_tens = minuend // 10
        minuend_ones = minuend % 10
        subtrahend_tens = subtrahend // 10
        subtrahend_ones = subtrahend % 10
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 识别同头数减法",
            operation="识别同头数",
            result=f"十位都是{minuend_tens}，使用同头数减法"
        ))
        
        steps.append(CalculationStep(
            description=f"分解：{minuend} = {minuend_tens}0 + {minuend_ones}, {subtrahend} = {subtrahend_tens}0 + {subtrahend_ones}",
            operation="数字分解",
            result=f"十位相同：{minuend_tens}，个位：{minuend_ones}-{subtrahend_ones}"
        ))
        
        # 十位相减（同头数相减为0）
        tens_result = 0
        ones_result = minuend_ones - subtrahend_ones
        
        steps.append(CalculationStep(
            description=f"十位相减：{minuend_tens} - {subtrahend_tens} = 0",
            operation="同头数相减",
            result=0
        ))
        
        steps.append(CalculationStep(
            description=f"个位相减：{minuend_ones} - {subtrahend_ones} = {ones_result}",
            operation="个位相减",
            result=ones_result
        ))
        
        final_result = tens_result * 10 + ones_result
        steps.append(CalculationStep(
            description=f"组合结果：0 + {ones_result} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="同头数减法：十位相同时，直接计算个位差"
        ))
        
        return steps