"""
几十一乘几十一实现
形如21×31的算法，公式(10a+1)(10b+1)=100ab+10(a+b)+1
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class TensOneMultiplication(MathCalculator):
    """几十一乘几十一算法"""
    
    def __init__(self):
        super().__init__("几十一乘法", "几十一乘几十一，前乘百和乘十再加一", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：形如21×31，个位数都是1"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否都是两位数且个位数都是1
            if 10 <= a <= 99 and 10 <= b <= 99:
                return a % 10 == 1 and b % 10 == 1
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建几十一乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 提取十位数字
        tens_a = a // 10
        tens_b = b // 10
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别几十一乘法：{a} 和 {b}",
            operation="识别模式",
            result=f"都是个位为1的两位数：{tens_a}1 × {tens_b}1"
        ))
        
        steps.append(CalculationStep(
            description=f"提取十位数：{tens_a} 和 {tens_b}",
            operation="分解数字",
            result=f"a={tens_a}, b={tens_b}"
        ))
        
        # 计算各部分
        hundreds_part = tens_a * tens_b * 100
        tens_part = (tens_a + tens_b) * 10
        ones_part = 1
        
        steps.append(CalculationStep(
            description=f"前乘百：{tens_a} × {tens_b} × 100 = {hundreds_part}",
            operation="计算百位部分",
            result=hundreds_part
        ))
        
        steps.append(CalculationStep(
            description=f"和乘十：({tens_a} + {tens_b}) × 10 = {tens_part}",
            operation="计算十位部分",
            result=tens_part
        ))
        
        steps.append(CalculationStep(
            description=f"再加一：+ 1",
            operation="加个位数",
            result=ones_part
        ))
        
        # 最终结果
        final_result = hundreds_part + tens_part + ones_part
        
        steps.append(CalculationStep(
            description=f"最终结果：{hundreds_part} + {tens_part} + {ones_part} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="(10a+1)(10b+1) = 100ab + 10(a+b) + 1"
        ))
        
        return steps