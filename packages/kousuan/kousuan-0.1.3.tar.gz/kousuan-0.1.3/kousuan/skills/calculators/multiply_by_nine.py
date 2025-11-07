"""
乘9及其重复数实现
一个数乘9、99、999等，先乘整十、整百数再减原数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByNine(MathCalculator):
    """乘9及其重复数"""
    
    def __init__(self):
        super().__init__("乘9速算", "一个数乘9、99、999等，先乘整数再减原数", priority=4)
    
    def _is_nine_pattern(self, num) -> tuple:
        """检查是否为9、99、999等模式，返回(是否匹配, 位数, 基数)"""
        num = int(num)
        if num <= 0:
            return False, 0, 0
        
        str_num = str(num)
        # 检查是否全为9
        if all(d == '9' for d in str_num):
            digits = len(str_num)
            base = 10 ** digits  # 10, 100, 1000等
            return True, digits, base
        
        return False, 0, 0
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：一个数乘以9、99、999等"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否有一个数是9的重复数
            is_nine_a, _, _ = self._is_nine_pattern(a)
            is_nine_b, _, _ = self._is_nine_pattern(b)
            
            return is_nine_a or is_nine_b
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘9速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是9的重复数，哪个是被乘数
        is_nine_a, digits_a, base_a = self._is_nine_pattern(a)
        is_nine_b, digits_b, base_b = self._is_nine_pattern(b)
        
        if is_nine_a:
            nine_num, digits, base = a, digits_a, base_a
            multiplied_num = b
        else:
            nine_num, digits, base = b, digits_b, base_b
            multiplied_num = a
        
        steps = []
        
        # 第一步：识别模式
        nine_str = '9' * digits
        steps.append(CalculationStep(
            description=f"识别乘{nine_str}模式：{multiplied_num} × {nine_num}",
            operation="识别模式",
            result=f"使用乘{nine_str}速算法"
        ))
        
        # 第二步：乘整数
        temp_result = multiplied_num * base
        if digits == 1:
            steps.append(CalculationStep(
                description=f"{multiplied_num} × 10 = {temp_result}",
                operation=f"先乘10",
                result=temp_result
            ))
        else:
            base_str = '1' + '0' * digits
            steps.append(CalculationStep(
                description=f"{multiplied_num} × {base_str} = {temp_result}",
                operation=f"先乘{base_str}",
                result=temp_result
            ))
        
        # 第三步：减原数
        final_result = temp_result - multiplied_num
        steps.append(CalculationStep(
            description=f"{temp_result} - {multiplied_num} = {final_result}",
            operation="减去原数",
            result=final_result,
            formula=f"数×{nine_str} = (数×{'1'+'0'*digits}) - 数"
        ))
        
        # 验证步骤（可选）
        if digits == 1:
            steps.append(CalculationStep(
                description=f"验证：{multiplied_num} × 9 = {final_result}",
                operation="验证结果",
                result="✓ 正确"
            ))
        
        return steps