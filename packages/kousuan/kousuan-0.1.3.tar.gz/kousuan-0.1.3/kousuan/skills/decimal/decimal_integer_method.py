"""
小数乘法整化法算子
去小数点乘后再补位的技巧
"""

from typing import List
from .decima_calculator import DecimaCalculator
from ..base_types import Formula, CalculationStep


class DecimalIntegerMethod(DecimaCalculator):
    """小数乘法整化法算子"""
    
    def __init__(self):
        super().__init__("小数整化乘法", "去小数点乘后再补位", priority=7)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：小数乘法"""
        if not super().is_match_pattern(formula):
            return False
        return formula.type == "multiplication"
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建整化乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 分析原始数据
        a_str, b_str = str(a), str(b)
        a_places = len(a_str.split('.')[1]) if '.' in a_str else 0
        b_places = len(b_str.split('.')[1]) if '.' in b_str else 0
        total_places = a_places + b_places
        
        steps.append(CalculationStep(
            description=f"分析：{a}({a_places}位小数) × {b}({b_places}位小数)",
            operation="分析小数位数",
            result=f"结果需要{total_places}位小数"
        ))
        
        # 去小数点转为整数
        a_int = int(a_str.replace('.', ''))
        b_int = int(b_str.replace('.', ''))
        
        steps.append(CalculationStep(
            description=f"去小数点：{a} × {b} → {a_int} × {b_int}",
            operation="转换为整数",
            result=f"{a_int} × {b_int}"
        ))
        
        # 整数相乘
        product_int = a_int * b_int
        steps.append(CalculationStep(
            description=f"整数相乘：{a_int} × {b_int} = {product_int}",
            operation="整数乘法",
            result=product_int
        ))
        
        # 恢复小数点
        final_result = product_int / (10 ** total_places)
        decimal_point_pos = len(str(product_int)) - total_places
        
        steps.append(CalculationStep(
            description=f"恢复小数点：从右数{total_places}位 → {final_result}",
            operation="恢复小数点",
            result=final_result,
            formula="整化法：去小数点 → 整数相乘 → 移动小数点"
        ))
        
        return steps
