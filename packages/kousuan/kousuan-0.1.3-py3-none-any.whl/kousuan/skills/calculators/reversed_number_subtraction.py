"""
颠倒数相减实现
两位数或多位数中数字顺序颠倒的数相减
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ReversedNumberSubtraction(MathCalculator):
    """颠倒数相减"""
    
    def __init__(self):
        super().__init__("颠倒数相减", "两位数颠倒数相减，差是9的倍数", priority=5)
        self.formula = "AB - BA = 9(A-B)"
    
    def _is_reversed_pair(self, a: int, b: int) -> bool:
        """判断是否为颠倒数对"""
        str_a = str(abs(a))
        str_b = str(abs(b))
        
        # 长度必须相同
        if len(str_a) != len(str_b):
            return False
        
        # 检查是否为颠倒关系
        return str_a == str_b[::-1]
    
    def _get_digit_difference(self, num) -> int:
        """获取首位数字与尾位数字的差"""
        str_num = str(abs(int(num)))
        if len(str_num) < 2:
            return 0
        
        first_digit = int(str_num[0])
        last_digit = int(str_num[-1])
        return abs(first_digit - last_digit)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个数互为颠倒数的减法"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 必须都是两位数及以上，且互为颠倒数
            return (abs(a) >= 10 and abs(b) >= 10 and 
                   self._is_reversed_pair(a, b))
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建颠倒数相减步骤"""
        numbers = formula.get_numbers()
        original_a, original_b = [elem.get_numeric_value() for elem in numbers]
        
        # 计算真实结果（保持原始顺序）
        actual_result = original_a - original_b
        
        # 为了分析数字特征，使用绝对值
        a, b = abs(original_a), abs(original_b)
        
        str_a = str(a)
        str_b = str(b)
        
        steps = []
        
        if len(str_a) == 2:
            # 两位数情况
            first_digit = int(str_a[0])
            last_digit = int(str_a[1])
            digit_diff = first_digit - last_digit
            
            # 计算基础差值（不带符号）
            base_result = abs(digit_diff) * 9
            
            steps.append(CalculationStep(
                description=f"识别颠倒数对：{original_a} 和 {original_b}（{str_a} 和 {str_b}）",
                operation="识别模式",
                result="颠倒数相减"
            ))
            
            steps.append(CalculationStep(
                description=f"十位数字 {first_digit}，个位数字 {last_digit}，差为 {digit_diff}",
                operation="计算数字差",
                result=digit_diff
            ))
            
            # 根据原始计算的符号确定结果
            if actual_result >= 0:
                steps.append(CalculationStep(
                    description=f"颠倒数相减 = （首位数字 - 尾位数字）× 9 = {digit_diff} × 9 = {actual_result}",
                    operation="应用公式",
                    result=actual_result,
                    formula="(首位 - 尾位) × 9"
                ))
            else:
                # 负数情况
                steps.append(CalculationStep(
                    description=f"由于 {original_a} < {original_b}，结果为负数",
                    operation="判断符号",
                    result="结果为负"
                ))
                
                steps.append(CalculationStep(
                    description=f"颠倒数相减 = -（首位数字 - 尾位数字）× 9 = -{abs(digit_diff)} × 9 = {actual_result}",
                    operation="应用公式",
                    result=actual_result,
                    formula="负数情况：-(首位 - 尾位) × 9"
                ))
        
        else:
            # 多位数情况（通用公式）
            digit_diff = self._get_digit_difference(a)
            
            steps.append(CalculationStep(
                description=f"识别颠倒数对：{original_a} 和 {original_b}",
                operation="识别模式", 
                result="颠倒数相减"
            ))
            
            steps.append(CalculationStep(
                description=f"首位数字与尾位数字的差：{digit_diff}",
                operation="计算数字差",
                result=digit_diff
            ))
            
            steps.append(CalculationStep(
                description=f"直接计算：{original_a} - {original_b} = {actual_result}",
                operation="直接计算",
                result=actual_result
            ))
            
            if actual_result != 0:
                steps.append(CalculationStep(
                    description=f"验证：{abs(actual_result)} ÷ 9 = {abs(actual_result) // 9}，确实是9的倍数",
                    operation="验证结果",
                    result=f"{abs(actual_result)}是9的{abs(actual_result) // 9}倍"
                ))
        
        return steps