"""
凑十法实现
20以内进位加法，将其中一个加数拆分成与另一个加数凑成10的数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class TenComplementAddition(MathCalculator):
    """凑十法（20以内进位加法）"""
    
    def __init__(self):
        super().__init__("凑十法", "20以内进位加法，将其中一个加数拆分成与另一个加数凑成10的数", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个20以内的数相加且需要进位"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            # 20以内的整数，且相加需要进位（结果>10）
            return (isinstance(a, int) and isinstance(b, int) and 
                   0 < a <= 20 and 0 < b <= 20 and a + b > 10 and a + b <= 20)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建凑十法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个数更接近10
        if a >= b:
            larger, smaller = a, b
        else:
            larger, smaller = b, a
        
        # 计算需要凑十的数
        complement = 10 - larger
        remainder = smaller - complement
        
        steps = [
            CalculationStep(
                description=f"观察发现 {larger} 和 {complement} 可以凑成 10",
                operation=f"寻找凑十数",
                result=f"{larger} + {complement} = 10"
            ),
            CalculationStep(
                description=f"将 {smaller} 拆分为 {complement} 和 {remainder}",
                operation=f"拆分小数",
                result=f"{smaller} = {complement} + {remainder}"
            ),
            CalculationStep(
                description=f"先算 {larger} + {complement} = 10",
                operation=f"凑十计算",
                result=10
            ),
            CalculationStep(
                description=f"再算 10 + {remainder} = {10 + remainder}",
                operation=f"加剩余数",
                result=10 + remainder
            )
        ]
        
        return steps