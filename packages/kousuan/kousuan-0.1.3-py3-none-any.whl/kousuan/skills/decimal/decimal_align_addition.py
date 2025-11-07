"""
小数对齐加法算子
实现对齐小数点的加法技巧
"""

from typing import List
from .decima_calculator import DecimaCalculator
from ..base_types import Formula, CalculationStep


class DecimalAlignAddition(DecimaCalculator):
    """小数对齐加法算子"""
    
    def __init__(self):
        super().__init__("小数对齐加法", "对齐小数点后相加，不够位的补0", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：小数加法"""
        if not super().is_match_pattern(formula):
            return False
        return formula.type == "addition"
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建对齐加法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 分析小数位数差异
        a_str, b_str = str(a), str(b)
        a_places = len(a_str.split('.')[1]) if '.' in a_str else 0
        b_places = len(b_str.split('.')[1]) if '.' in b_str else 0
        
        steps.append(CalculationStep(
            description=f"分析：{a}有{a_places}位小数，{b}有{b_places}位小数",
            operation="分析小数位数",
            result=f"需要补零对齐"
        ))
        
        # 对齐小数点
        a_aligned, b_aligned = self._align_decimals(a, b)
        steps.append(CalculationStep(
            description=f"补零对齐：{a} + {b} = {a_aligned} + {b_aligned}",
            operation="补零对齐",
            result=f"{a_aligned} + {b_aligned}"
        ))
        
        # 列竖式计算
        result = a + b
        steps.append(CalculationStep(
            description=f"列竖式相加：{a_aligned} + {b_aligned} = {result}",
            operation="列竖式相加",
            result=result,
            formula="小数加法：小数点对齐 → 补零 → 按位相加"
        ))
        
        return steps
