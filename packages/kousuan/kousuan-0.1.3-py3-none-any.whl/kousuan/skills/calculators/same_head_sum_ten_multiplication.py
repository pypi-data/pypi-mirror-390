"""
同头尾合十乘法实现
十位相同、个位相加为10的两位数相乘
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SameHeadSumTenMultiplication(MathCalculator):
    """同头尾合十乘法"""
    
    def __init__(self):
        super().__init__("同头尾合十", "十位相同、个位相加为10的两位数相乘", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：十位相同、个位和为10的两位数相乘"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 两位数且十位相同、个位和为10
            if 10 <= a <= 99 and 10 <= b <= 99:
                a_tens, a_ones = a // 10, a % 10
                b_tens, b_ones = b // 10, b % 10
                return a_tens == b_tens and a_ones + b_ones == 10
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建同头尾合十步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 分解数字
        tens_digit = a // 10
        a_ones = a % 10
        b_ones = b % 10
        
        # 计算
        head_calc = tens_digit * (tens_digit + 1)
        tail_calc = a_ones * b_ones
        result = head_calc * 100 + tail_calc
        
        steps = [
            CalculationStep(
                description=f"同头尾合十: 十位数字相同({tens_digit})，个位数字相加为10({a_ones}+{b_ones}=10)",
                operation="识别模式",
                result="满足同头尾合十条件"
            ),
            CalculationStep(
                description=f"计算头×(头+1)：{tens_digit}×{tens_digit+1}={head_calc}",
                operation="头部计算",
                result=head_calc
            ),
            CalculationStep(
                description=f"计算尾×尾：{a_ones}×{b_ones}={tail_calc}",
                operation="尾部计算", 
                result=tail_calc
            ),
            CalculationStep(
                description=f"组合结果：{head_calc}|{tail_calc:02d}={result}",
                operation="结果组合",
                result=result,
                formula="头×(头+1)×100 + 尾×尾"
            )
        ]
        
        return steps