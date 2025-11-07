"""
小数除法除数化整算子
把除数变成整数，被除数同步扩大
"""

from typing import List
from .decima_calculator import DecimaCalculator
from ..base_types import Formula, CalculationStep


class DecimalDivisorInteger(DecimaCalculator):
    """小数除法除数化整算子"""
    
    def __init__(self):
        super().__init__("除数化整法", "把除数变成整数，被除数同步扩大", priority=7)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：小数除法且除数是小数"""
        if not super().is_match_pattern(formula):
            return False
        
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            # 除数是小数
            return isinstance(b, float) and not b.is_integer()
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建除数化整步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 分析除数
        b_str = str(b)
        decimal_places = len(b_str.split('.')[1]) if '.' in b_str else 0
        scale_factor = 10 ** decimal_places
        
        steps.append(CalculationStep(
            description=f"除数{b}有{decimal_places}位小数，需要扩大{scale_factor}倍化为整数",
            operation="分析除数",
            result=f"扩大倍数：{scale_factor}"
        ))
        
        # 同时扩大被除数和除数
        a_scaled = a * scale_factor
        b_scaled = b * scale_factor
        
        steps.append(CalculationStep(
            description=f"同时扩大{scale_factor}倍：{a} ÷ {b} → {a_scaled} ÷ {b_scaled}",
            operation="同时扩大",
            result=f"{a_scaled} ÷ {b_scaled}"
        ))
        
        # 验证除数已为整数
        steps.append(CalculationStep(
            description=f"验证：除数{b_scaled}已为整数",
            operation="验证转换",
            result="除数已为整数，可按整数除法计算"
        ))
        
        # 执行除法
        final_result = a_scaled / b_scaled
        steps.append(CalculationStep(
            description=f"执行除法：{a_scaled} ÷ {b_scaled} = {final_result}",
            operation="执行除法",
            result=final_result,
            formula="除数化整法：同时扩大 → 除数变整数 → 商不变"
        ))
        
        return steps
