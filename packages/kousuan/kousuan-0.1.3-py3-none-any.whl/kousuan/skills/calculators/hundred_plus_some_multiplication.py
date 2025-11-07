"""
一百零几乘一百零几实现
利用(100+a)(100+b)=10000+100(a+b)+ab的公式
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class HundredPlusSomeMultiplication(MathCalculator):
    """一百零几乘一百零几算法"""
    
    def __init__(self):
        super().__init__("一百零几乘法", "一百零几乘一百零几，一万加百倍和再加积", priority=3)
        self.formula = "(100+a)(100+b) = 10000 + 100(a+b) + ab"
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：形如103×107的一百零几乘法"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否都在100-109范围内（一百零几）
            return 100 <= a <= 109 and 100 <= b <= 109
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建一百零几乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 提取超出100的部分
        excess_a = a - 100
        excess_b = b - 100
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别一百零几乘法：{a} × {b}",
            operation="识别模式",
            result=f"形式：(100+{excess_a}) × (100+{excess_b})"
        ))
        
        steps.append(CalculationStep(
            description=f"分解数字：{a} = 100 + {excess_a}，{b} = 100 + {excess_b}",
            operation="提取偏差",
            result=f"a={excess_a}, b={excess_b}"
        ))
        
        # 计算各部分
        base_part = 10000  # 100 × 100
        sum_part = 100 * (excess_a + excess_b)  # 100(a+b)
        product_part = excess_a * excess_b  # ab
        
        steps.append(CalculationStep(
            description=f"基数部分：100 × 100 = {base_part}",
            operation="计算基数",
            result=base_part
        ))
        
        steps.append(CalculationStep(
            description=f"百倍和：100 × ({excess_a} + {excess_b}) = 100 × {excess_a + excess_b} = {sum_part}",
            operation="计算百倍和",
            result=sum_part
        ))
        
        steps.append(CalculationStep(
            description=f"偏差积：{excess_a} × {excess_b} = {product_part}",
            operation="计算偏差积",
            result=product_part
        ))
        
        # 最终结果
        final_result = base_part + sum_part + product_part
        
        steps.append(CalculationStep(
            description=f"最终结果：{base_part} + {sum_part} + {product_part} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="(100+a)(100+b) = 10000 + 100(a+b) + ab"
        ))
        
        return steps