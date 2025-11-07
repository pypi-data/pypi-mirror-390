"""
乘以125实现
利用125 = 1000/8的特点，转换为除以8再乘1000
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByOneHundredTwentyFive(MathCalculator):
    """乘以125算法"""
    
    def __init__(self):
        super().__init__("乘125速算", "任意整数乘125，除以8再添三个0", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数乘以125"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 检查是否有一个数是125
            return a == 125 or b == 125
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘125速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是125，哪个是被乘数
        if a == 125:
            multiplied_num = b
        else:
            multiplied_num = a
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 125 使用乘125速算法",
            operation="识别模式",
            result="125 = 1000 ÷ 8，转换为除8乘1000"
        ))
        
        # 检查是否能被8整除
        if multiplied_num % 8 == 0:
            quotient = int(multiplied_num // 8)
            steps.append(CalculationStep(
                description=f"{multiplied_num} ÷ 8 = {quotient}",
                operation="除以8",
                result=f"{quotient}"
            ))
            
            final_result = quotient * 1000
            steps.append(CalculationStep(
                description=f"{quotient} × 1000 = {final_result}",
                operation="乘以1000",
                result=final_result,
                formula="a × 125 = (a ÷ 8) × 1000"
            ))
        else:
            # 不能被8整除，转换为小数计算
            quotient = multiplied_num / 8
            steps.append(CalculationStep(
                description=f"{multiplied_num} ÷ 8 = {quotient}",
                operation="除以8",
                result=f"{quotient}"
            ))
            
            final_result = quotient * 1000
            if final_result.is_integer():
                final_result = int(final_result)
            
            steps.append(CalculationStep(
                description=f"{quotient} × 1000 = {final_result}",
                operation="乘以1000",
                result=final_result,
                formula="a × 125 = (a ÷ 8) × 1000"
            ))
        
        return steps