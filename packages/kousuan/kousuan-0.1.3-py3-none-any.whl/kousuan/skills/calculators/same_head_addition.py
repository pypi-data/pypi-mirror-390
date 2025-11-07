"""
同头数加法实现
处理十位相同的两位数加法，如47+43=90
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SameHeadAddition(MathCalculator):
    """同头数加法算法"""
    
    def __init__(self):
        super().__init__("同头数加法", "十位相同的两位数加法", priority=7)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：十位相同的两位数加法"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, int) and isinstance(addend2, int)):
                return False
            
            # 两位数且十位相同
            if not (10 <= addend1 <= 99 and 10 <= addend2 <= 99):
                return False
            
            addend1_tens = addend1 // 10
            addend2_tens = addend2 // 10
            
            # 十位相同
            return addend1_tens == addend2_tens
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建同头数加法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        addend1_tens = addend1 // 10
        addend1_ones = addend1 % 10
        addend2_tens = addend2 // 10
        addend2_ones = addend2 % 10
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 识别同头数加法",
            operation="识别同头数",
            result=f"十位都是{addend1_tens}，使用同头数加法"
        ))
        
        steps.append(CalculationStep(
            description=f"分解：{addend1} = {addend1_tens}0 + {addend1_ones}, {addend2} = {addend2_tens}0 + {addend2_ones}",
            operation="数字分解",
            result=f"十位相同：{addend1_tens}，个位：{addend1_ones}+{addend2_ones}"
        ))
        
        # 十位相加
        tens_sum = addend1_tens + addend2_tens
        ones_sum = addend1_ones + addend2_ones
        
        steps.append(CalculationStep(
            description=f"十位相加：{addend1_tens} + {addend2_tens} = {tens_sum}",
            operation="十位相加",
            result=tens_sum
        ))
        
        steps.append(CalculationStep(
            description=f"个位相加：{addend1_ones} + {addend2_ones} = {ones_sum}",
            operation="个位相加",
            result=ones_sum
        ))
        
        # 处理进位
        if ones_sum >= 10:
            carry = ones_sum // 10
            final_ones = ones_sum % 10
            final_tens = tens_sum + carry
            
            steps.append(CalculationStep(
                description=f"个位进位：{ones_sum} = {carry}0 + {final_ones}，十位变为 {tens_sum} + {carry} = {final_tens}",
                operation="处理进位",
                result=f"十位：{final_tens}，个位：{final_ones}"
            ))
            
            final_result = final_tens * 10 + final_ones
        else:
            final_result = tens_sum * 10 + ones_sum
            
        steps.append(CalculationStep(
            description=f"组合结果：{final_result}",
            operation="合并结果",
            result=final_result,
            formula="同头数加法：AB + AC = A×10×2 + (B+C)"
        ))
        
        return steps