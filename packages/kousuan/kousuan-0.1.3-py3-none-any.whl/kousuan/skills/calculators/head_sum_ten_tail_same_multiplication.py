"""
头合十尾相同乘法实现
十位相加为10、个位相同的两位数相乘
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class HeadSumTenTailSameMultiplication(MathCalculator):
    """头合十尾相同乘法"""
    
    def __init__(self):
        super().__init__("头合十尾相同", "十位相加为10、个位相同的两位数相乘", priority=2)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：十位和为10、个位相同的两位数相乘"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 两位数且十位和为10、个位相同
            if 10 <= a <= 99 and 10 <= b <= 99:
                a_tens, a_ones = a // 10, a % 10
                b_tens, b_ones = b // 10, b % 10
                return a_tens + b_tens == 10 and a_ones == b_ones
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建头合十尾相同步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 分解数字
        a_tens, a_ones = a // 10, a % 10
        b_tens, b_ones = b // 10, b % 10
        
        # 计算
        head_calc = a_tens * b_tens + a_ones
        tail_calc = a_ones * b_ones
        result = head_calc * 100 + tail_calc
        
        steps = [
            CalculationStep(
                description=f"头合十尾相同: 十位数字相加为10({a_tens}+{b_tens}=10)，个位数字相同({a_ones})",
                operation="识别模式",
                result="满足头合十尾相同条件"
            ),
            CalculationStep(
                description=f"计算头×头+尾：{a_tens}×{b_tens}+{a_ones}={a_tens*b_tens}+{a_ones}={head_calc}",
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
                formula="(头×头+尾)×100 + 尾×尾"
            )
        ]
        
        return steps