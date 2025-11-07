"""
除以5实现
一个数除以5，可先乘2再除以10，或先除以10再乘2
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class DivideByFive(MathCalculator):
    """除以5算法"""
    
    def __init__(self):
        super().__init__("除以5速算", "一个数除以5，先乘2再除以10", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任何数除以5"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            # 被除数是任意数，除数必须是5
            return (isinstance(a, (int, float)) and 
                   isinstance(b, (int, float)) and 
                   b == 5)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建除以5速算步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ 5 使用除5速算法",
            operation="识别模式",
            result="使用先乘2再除以10的方法"
        ))
        
        # 方法1：先乘2再除以10
        temp_result = dividend * 2
        steps.append(CalculationStep(
            description=f"{dividend} × 2 = {temp_result}",
            operation="先乘2",
            result=temp_result
        ))
        
        final_result = temp_result / 10
        steps.append(CalculationStep(
            description=f"{temp_result} ÷ 10 = {final_result}",
            operation="再除以10",
            result=final_result,
            formula="数÷5 = (数×2)÷10"
        ))
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
            steps[-1].result = final_result
        
        return steps