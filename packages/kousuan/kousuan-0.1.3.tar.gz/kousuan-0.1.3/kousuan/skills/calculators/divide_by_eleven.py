"""
除以11实现
利用11的特殊性质进行快速计算
包括奇偶位差规律和分拆方法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class DivideByEleven(MathCalculator):
    """除以11算法"""
    
    def __init__(self):
        super().__init__("除11速算", "十一分法，看奇偶位差", priority=6)
    
    def _alternating_sum(self, num: int) -> int:
        """计算奇偶位交替和（用于11整除性判断）"""
        digits = [int(d) for d in str(num)]
        alternating_sum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 0:
                alternating_sum += digit
            else:
                alternating_sum -= digit
        return alternating_sum
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数除以11"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            return isinstance(divisor, (int, float)) and divisor == 11
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建除以11速算步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 确保被除数是整数
        if isinstance(dividend, float) and dividend.is_integer():
            dividend = int(dividend)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ 11 使用除11速算法",
            operation="识别除以11",
            result="十一分法，看奇偶位差"
        ))
        
        if isinstance(dividend, int) and dividend >= 11:
            # 方法1：奇偶位差判断法（用于判断整除性）
            if dividend <= 9999:  # 对于不太大的数使用此方法
                digits_str = str(dividend)
                digits = [int(d) for d in digits_str]
                
                # 计算奇偶位差
                odd_sum = sum(digits[i] for i in range(0, len(digits), 2))  # 奇数位（从右往左数）
                even_sum = sum(digits[i] for i in range(1, len(digits), 2))  # 偶数位
                alternating_diff = self._alternating_sum(dividend)
                
                steps.append(CalculationStep(
                    description=f"奇偶位分析：{digits_str}",
                    operation="分析奇偶位",
                    result=f"从右往左：奇数位={odd_sum}, 偶数位={even_sum}"
                ))
                
                steps.append(CalculationStep(
                    description=f"奇偶位差：{odd_sum} - {even_sum} = {alternating_diff}",
                    operation="计算位差",
                    result=f"位差为 {alternating_diff}"
                ))
                
                if alternating_diff % 11 == 0:
                    quotient = dividend // 11
                    steps.append(CalculationStep(
                        description=f"位差{alternating_diff}能被11整除，所以{dividend}能被11整除",
                        operation="整除判断",
                        result=f"{dividend} ÷ 11 = {quotient}"
                    ))
                    final_result = quotient
                else:
                    quotient = dividend // 11
                    remainder = dividend % 11
                    steps.append(CalculationStep(
                        description=f"位差{alternating_diff}不能被11整除，有余数",
                        operation="有余数",
                        result=f"商 {quotient}，余数 {remainder}"
                    ))
                    final_result = dividend / 11
            else:
                # 对于大数，直接计算
                final_result = dividend / 11
                
            # 方法2：分拆法（用于心算）
            if dividend >= 22 and dividend <= 999:
                # 寻找11的倍数进行分拆
                largest_multiple = (dividend // 11) * 11
                remainder_part = dividend - largest_multiple
                
                if largest_multiple > 0 and remainder_part != dividend:
                    steps.append(CalculationStep(
                        description=f"分拆法：{dividend} = {largest_multiple} + {remainder_part}",
                        operation="分拆方法",
                        result=f"{largest_multiple} ÷ 11 + {remainder_part} ÷ 11 = {largest_multiple//11} + {remainder_part/11}"
                    ))
            
            # 方法3：心算技巧（对于小数）
            if dividend <= 132:  # 11 × 12 = 132
                quotient_estimate = dividend // 11
                if quotient_estimate <= 12:
                    steps.append(CalculationStep(
                        description=f"心算技巧：11的倍数表 - 11×{quotient_estimate}={11*quotient_estimate}",
                        operation="倍数表",
                        result=f"最接近{dividend}的11的倍数"
                    ))
        else:
            # 小数或浮点数
            final_result = dividend / 11
            steps.append(CalculationStep(
                description=f"直接计算：{dividend} ÷ 11 = {final_result}",
                operation="直接计算",
                result=final_result
            ))
        
        # 确保final_result已定义
        if 'final_result' not in locals():
            final_result = dividend / 11
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ 11 = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="除以11：奇偶位差判断 + 分拆法"
        ))
        
        # 验证（如果是整除）
        if isinstance(final_result, int) and dividend <= 999:
            verification = final_result * 11
            if verification == dividend:
                steps.append(CalculationStep(
                    description=f"验证：{final_result} × 11 = {verification}",
                    operation="验证正确",
                    result="✓ 计算正确"
                ))
        
        return steps