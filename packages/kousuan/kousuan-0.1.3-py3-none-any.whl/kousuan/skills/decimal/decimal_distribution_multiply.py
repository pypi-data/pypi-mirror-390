"""
小数分配律乘法算子
拆分为整数部分和小数部分相乘再加
"""

from typing import List
from .decima_calculator import DecimaCalculator
from ..base_types import Formula, CalculationStep


class DecimalDistributionMultiply(DecimaCalculator):
    """小数分配律乘法算子"""
    
    def __init__(self):
        super().__init__("小数分配律乘法", "拆分为整数部分和小数部分相乘再加", priority=6)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：小数乘法且至少有一个数可以拆分为整数+小数"""
        if not super().is_match_pattern(formula):
            return False
        
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 检查是否有数字可以方便地拆分（整数部分较大，小数部分简单）
        return self._can_split_conveniently(a) or self._can_split_conveniently(b)
    
    def _can_split_conveniently(self, num: float) -> bool:
        """判断数字是否适合用分配律拆分"""
        if isinstance(num, int):
            return False
        
        integer_part = int(num)
        decimal_part = num - integer_part
        
        # 整数部分>=1且小数部分简单（如0.1, 0.2, 0.5等）
        return integer_part >= 1 and decimal_part in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建分配律乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 确定哪个数适合拆分
        if self._can_split_conveniently(a):
            split_num, other_num = a, b
            split_name, other_name = "第一个数", "第二个数"
        else:
            split_num, other_num = b, a
            split_name, other_name = "第二个数", "第一个数"
        
        # 拆分数字
        integer_part = int(split_num)
        decimal_part = split_num - integer_part
        
        steps.append(CalculationStep(
            description=f"拆分{split_name}：{split_num} = {integer_part} + {decimal_part}",
            operation="拆分数字",
            result=f"{integer_part} + {decimal_part}"
        ))
        
        # 应用分配律
        steps.append(CalculationStep(
            description=f"应用分配律：{split_num} × {other_num} = ({integer_part} + {decimal_part}) × {other_num}",
            operation="应用分配律",
            result=f"{integer_part} × {other_num} + {decimal_part} × {other_num}"
        ))
        
        # 计算整数部分乘积
        integer_product = integer_part * other_num
        steps.append(CalculationStep(
            description=f"整数部分：{integer_part} × {other_num} = {integer_product}",
            operation="计算整数部分",
            result=integer_product
        ))
        
        # 计算小数部分乘积
        decimal_product = decimal_part * other_num
        steps.append(CalculationStep(
            description=f"小数部分：{decimal_part} × {other_num} = {decimal_product}",
            operation="计算小数部分",
            result=decimal_product
        ))
        
        # 相加得到最终结果
        final_result = integer_product + decimal_product
        steps.append(CalculationStep(
            description=f"相加：{integer_product} + {decimal_product} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="分配律：(a+b)×c = a×c + b×c"
        ))
        
        return steps
