"""
乘以19实现
乘以19，等于原数乘以20再减去原数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByNineteen(MathCalculator):
    """乘以19算法"""
    
    def __init__(self):
        super().__init__("乘19速算", "乘以19等于乘20再减原数", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数乘以19"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 检查是否有一个数是19
            return a == 19 or b == 19
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘19速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是19，哪个是被乘数
        if a == 19:
            multiplied_num = b
        else:
            multiplied_num = a
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 19 使用乘19速算法",
            operation="识别模式",
            result="19 = 20 - 1，转换为乘20减原数"
        ))
        
        # 计算乘以20
        times_twenty = multiplied_num * 20
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 20 = {times_twenty}",
            operation="乘以20",
            result=times_twenty
        ))
        
        # 减去原数得到最终结果
        final_result = times_twenty - multiplied_num
        steps.append(CalculationStep(
            description=f"{times_twenty} - {multiplied_num} = {final_result}",
            operation="减去原数",
            result=final_result,
            formula="a × 19 = a × 20 - a"
        ))
        
        return steps