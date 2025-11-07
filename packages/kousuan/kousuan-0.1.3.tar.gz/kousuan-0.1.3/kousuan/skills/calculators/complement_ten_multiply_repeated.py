"""
合十数乘两位重复数实现
合十数对：个位数字相加等于10的一对数，如73和77（3+7=10）
重复数：两位数中十位和个位相同，如11, 22, 33...99
规律：合十数对中的一个数乘以重复数 = 个位数字乘积 × 重复数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ComplementTenMultiplyRepeated(MathCalculator):
    """合十数乘两位重复数算法"""
    
    def __init__(self):
        super().__init__("合十数乘重复数", "合十数乘两位重复数，积的规律", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：合十数乘两位重复数"""
        if formula.type != "multiplication":
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
            
            # 检查是否有重复数（11, 22, 33...99）
            def is_repeated_number(num):
                str_num = str(num)
                return len(str_num) == 2 and str_num[0] == str_num[1]
            
            # 检查是否是合十数对
            def is_complement(num1):
                ones1, tens1 = num1 % 10, num1 // 10
                return ones1 + tens1 == 10

            # 如果a是重复数，b是合十数
            if is_repeated_number(a):
                return is_complement(b)
            # 如果b是重复数，a是合十数
            if is_repeated_number(b):
                return is_complement(a)
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建合十数乘重复数步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是重复数，哪个是合十数
        def is_repeated_number(num):
            str_num = str(num)
            return len(str_num) == 2 and str_num[0] == str_num[1]
        
        if is_repeated_number(a):
            repeated_num = a
            complement_num = b
        else:
            repeated_num = b
            complement_num = a
        
        # 分解数字：合十数 = A×10 + B，重复数 = C×10 + C
        A = complement_num // 10
        B = complement_num % 10
        C = repeated_num // 10  # 重复数的数字
        
        # 计算合十数对
        complement_pair_ones = 10 - B
        complement_pair = A * 10 + complement_pair_ones
        
        steps = []
        
        # 步骤1：识别模式
        steps.append(CalculationStep(
            description=f"识别合十数乘重复数：{complement_num} × {repeated_num}",
            operation="识别模式",
            result=f"{complement_num}是合十数，{repeated_num}是重复数"
        ))
        
        # 步骤2：验证合十
        steps.append(CalculationStep(
            description=f"分析：{complement_num}={A}x10+{B}并且{A}+{B}=10",
            operation="验证合十",
            result=f"合十数是：{complement_num}"
        ))
        
        # 步骤3：应用公式 (A×10 + B) × (C×10 + C) = (A+1) × C × 100 + B × C
        first_part = (A + 1) * C * 100
        second_part = B * C
        final_result = first_part + second_part
        
        steps.append(CalculationStep(
            description=f"应用公式：(A×10+B) × (C×10+C) = (A+1) × C × 100 + B × C",
            operation="应用公式",
            result=f"= {A+1}×{C}×100 + {B}×{C} = {first_part} + {second_part}",
            formula=f"({A}×10+{B}) × ({C}×10+{C}) = ({A}+1)×{C}×100 + {B}×{C}"
        ))
        
        # 步骤4：计算最终结果
        steps.append(CalculationStep(
            description=f"计算结果：{first_part} + {second_part} = {final_result}",
            operation="计算结果",
            result=final_result
        ))
        
        return steps