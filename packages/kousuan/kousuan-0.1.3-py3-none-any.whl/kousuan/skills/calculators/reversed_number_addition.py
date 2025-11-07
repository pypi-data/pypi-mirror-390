"""
颠倒数加法实现
形如AB + BA = 11(a+b)的算法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ReversedNumberAddition(MathCalculator):
    """颠倒数加法算法"""
    
    def __init__(self):
        super().__init__("颠倒数加法", "两位数颠倒数相加，和乘11", priority=6)
        self.formula = "AB + BA = 11(a+b)"
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：形如47+74的颠倒数加法"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否都是两位数
            if not (10 <= a <= 99 and 10 <= b <= 99):
                return False
            
            # 检查是否是颠倒数
            a_str = str(a)
            b_str = str(b)
            
            # 颠倒a看是否等于b
            return a_str == b_str[::-1]
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建颠倒数加法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 提取数字位
        a_tens = a // 10
        a_ones = a % 10
        b_tens = b // 10
        b_ones = b % 10
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别颠倒数加法：{a} + {b}",
            operation="识别模式",
            result=f"{a_tens}{a_ones} + {b_tens}{b_ones} 是颠倒数"
        ))
        
        steps.append(CalculationStep(
            description=f"提取数字位：{a} = {a_tens}和{a_ones}，{b} = {b_tens}和{b_ones}",
            operation="分解数字",
            result=f"验证：{a_tens} = {b_ones}, {a_ones} = {b_tens}"
        ))
        
        # 计算各位数字之和
        digits_sum = a_tens + a_ones  # 注意：对于颠倒数，a_tens + a_ones = b_tens + b_ones
        
        steps.append(CalculationStep(
            description=f"各位数字之和：{a_tens} + {a_ones} = {digits_sum}",
            operation="计算数字和",
            result=digits_sum
        ))
        
        # 应用公式
        final_result = 11 * digits_sum
        
        steps.append(CalculationStep(
            description=f"应用公式：11 × {digits_sum} = {final_result}",
            operation="乘以11",
            result=final_result,
            formula="AB + BA = 11(a+b)"
        ))
        
        return steps