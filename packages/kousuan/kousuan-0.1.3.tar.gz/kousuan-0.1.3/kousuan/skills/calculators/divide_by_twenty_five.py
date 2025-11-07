"""
除以25实现
利用25 = 100/4的特点，转换为乘以4再除以100
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class DivideByTwentyFive(MathCalculator):
    """除以25算法"""
    
    def __init__(self):
        super().__init__("除25速算", "除以25转换为乘4除100", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数除以25"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否是除以25
            return b == 25
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建除25速算步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ 25 使用除25速算法",
            operation="识别模式",
            result="25 = 100 ÷ 4，转换为乘4除100"
        ))
        
        # 乘以4
        product = dividend * 4
        steps.append(CalculationStep(
            description=f"{dividend} × 4 = {product}",
            operation="乘以4",
            result=f"{product}"
        ))
        
        # 除以100
        if product % 100 == 0:
            final_result = product // 100
            steps.append(CalculationStep(
                description=f"{product} ÷ 100 = {final_result}",
                operation="除以100",
                result=final_result,
                formula="a ÷ 25 = (a × 4) ÷ 100"
            ))
        else:
            final_result = product / 100
            steps.append(CalculationStep(
                description=f"{product} ÷ 100 = {final_result}",
                operation="除以100",
                result=final_result,
                formula="a ÷ 25 = (a × 4) ÷ 100"
            ))
        
        return steps