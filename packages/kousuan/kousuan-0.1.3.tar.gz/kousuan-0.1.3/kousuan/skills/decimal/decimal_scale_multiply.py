"""
小数倍数乘法算子
实现×10、×100、×0.1、×0.01的小数点移动规律
"""

from typing import List
from .decima_calculator import DecimaCalculator
from ..base_types import Formula, CalculationStep


class DecimalScaleMultiply(DecimaCalculator):
    """小数倍数乘法算子"""
    
    def __init__(self):
        super().__init__("小数点移动乘法", "乘10、100、0.1、0.01规律", priority=8)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：小数乘法且其中一个因数是10的幂或其倒数"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            
            # 检查是否有一个数是10的幂或其倒数
            scale_factors = [10, 100, 1000, 0.1, 0.01, 0.001]
            return a in scale_factors or b in scale_factors
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建倍数乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 确定哪个是倍数，哪个是普通数
        scale_factors = [10, 100, 1000, 0.1, 0.01, 0.001]
        if a in scale_factors:
            scale_factor, base_num = a, b
        else:
            scale_factor, base_num = b, a
        
        # 分析移动规律
        if scale_factor >= 1:
            # ×10, ×100等：右移小数点
            power = int(scale_factor).bit_length() - 1 if int(scale_factor) > 0 else 0
            if scale_factor == 10:
                power = 1
            elif scale_factor == 100:
                power = 2
            elif scale_factor == 1000:
                power = 3
            
            steps.append(CalculationStep(
                description=f"{base_num} × {scale_factor}，小数点右移{power}位",
                operation="分析移动规律",
                result=f"右移{power}位"
            ))
            
            final_result = base_num * scale_factor
            steps.append(CalculationStep(
                description=f"右移{power}位：{base_num} → {final_result}",
                operation="移动小数点",
                result=final_result,
                formula=f"×{scale_factor} = 小数点右移{power}位"
            ))
        else:
            # ×0.1, ×0.01等：左移小数点
            power = len(str(scale_factor).split('.')[1]) if '.' in str(scale_factor) else 0
            
            steps.append(CalculationStep(
                description=f"{base_num} × {scale_factor}，小数点左移{power}位",
                operation="分析移动规律",
                result=f"左移{power}位"
            ))
            
            final_result = base_num * scale_factor
            steps.append(CalculationStep(
                description=f"左移{power}位：{base_num} → {final_result}",
                operation="移动小数点",
                result=final_result,
                formula=f"×{scale_factor} = 小数点左移{power}位"
            ))
        
        return steps
