"""
以整数为中间数的整数乘法实现
利用(M-x)(M+x)=M²-x²的对称公式
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MiddleNumberMultiplication(MathCalculator):
    """以整数为中间数的乘法算法"""
    
    def __init__(self):
        super().__init__("中间数乘法", "对称分布数相乘，中数平方减差平方", priority=2)
    
    def _find_middle_number(self, a: int, b: int) -> tuple:
        """找到合适的中间数，优先选择末尾是0或5的数，返回(中间数, a的偏差, b的偏差)"""
        mid_number = (a + b) // 2
        return (mid_number, a - mid_number, b - mid_number)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：末尾数是0或5且两个数的差值（补数）绝对值相同"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查数值范围（不限制为两位数，支持更大范围）
            if not (10 <= a <= 99999 and 10 <= b <= 99999):
                return False
            
            # 寻找合适的中间数
            middle, diff_a, diff_b = self._find_middle_number(a, b)
            
            # 检查中间数是否为整十数、整百数、整千数，或末尾数是5
            middle_last_digit = middle % 10
            if middle_last_digit not in [0, 5]:
                return False
                
            # 检查两个差值（补数）的绝对值是否相同
            if abs(diff_a) != abs(diff_b):
                return False
            
            # 确保差值是合理范围内（不超过50）
            return abs(diff_a) <= 50 and diff_a * diff_b < 0
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建中间数乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确保是整数
        a_int = int(a)
        b_int = int(b)
        
        # 找到中间数
        middle, diff_a, diff_b = self._find_middle_number(a_int, b_int)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别对称乘法：{a_int} × {b_int}",
            operation="识别模式",
            result=f"寻找中间数进行对称分解"
        ))
        
        steps.append(CalculationStep(
            description=f"确定中间数：{middle}",
            operation="选择中间数",
            result=f"{a_int} = {middle} + ({diff_a}), {b_int} = {middle} + ({diff_b})"
        ))
        
        if diff_a * diff_b < 0 and abs(diff_a) == abs(diff_b):
            # 完美对称情况：(M-x)(M+x) = M² - x²
            x = abs(diff_a)
            middle_square = middle * middle
            x_square = x * x
            final_result = middle_square - x_square
            
            steps.append(CalculationStep(
                description=f"应用对称公式：({middle}-{x}) × ({middle}+{x})",
                operation="对称展开",
                result=f"= {middle}² - {x}²"
            ))
            
            steps.append(CalculationStep(
                description=f"计算：{middle}² - {x}² = {middle_square} - {x_square} = {final_result}",
                operation="计算结果",
                result=final_result,
                formula="(M-x)(M+x) = M² - x²"
            ))
        else:
            # 近似对称情况：使用分配律
            # (M+a)(M+b) = M² + M(a+b) + ab
            sum_diff = diff_a + diff_b
            product_diff = diff_a * diff_b
            middle_square = middle * middle
            middle_sum_part = middle * sum_diff
            final_result = middle_square + middle_sum_part + product_diff
            
            steps.append(CalculationStep(
                description=f"应用展开公式：({middle}+{diff_a}) × ({middle}+{diff_b})",
                operation="分配律展开",
                result=f"= {middle}² + {middle}×({diff_a}+{diff_b}) + {diff_a}×{diff_b}"
            ))
            
            steps.append(CalculationStep(
                description=f"计算各部分：{middle}² = {middle_square}, {middle}×{sum_diff} = {middle_sum_part}, {diff_a}×{diff_b} = {product_diff}",
                operation="分部计算",
                result=f"{middle_square} + {middle_sum_part} + {product_diff}"
            ))
            
            steps.append(CalculationStep(
                description=f"最终结果：{middle_square} + {middle_sum_part} + {product_diff} = {final_result}",
                operation="合并结果",
                result=final_result,
                formula="(M+a)(M+b) = M² + M(a+b) + ab"
            ))
        
        return steps