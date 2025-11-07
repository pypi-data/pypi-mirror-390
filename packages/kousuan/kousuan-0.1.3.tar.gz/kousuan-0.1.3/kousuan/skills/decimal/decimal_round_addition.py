"""
小数凑整加法算子
实现先凑整再加法的技巧
"""

from typing import List
from .decima_calculator import DecimaCalculator
from ..base_types import Formula, CalculationStep


class DecimalRoundAddition(DecimaCalculator):
    """小数凑整加法算子"""
    
    def __init__(self):
        super().__init__("小数凑整加法", "调整数字凑整数后加减", priority=6)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：小数加法且至少有一个数接近整数"""
        if not super().is_match_pattern(formula):
            return False
        
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 检查是否有数字接近整数（小数部分接近0或1）
        return self._can_round_to_integer(a) or self._can_round_to_integer(b)
    
    def _can_round_to_integer(self, num: float) -> bool:
        """判断数字是否适合凑整"""
        if isinstance(num, int):
            return False
        
        decimal_part = num - int(num)
        # 小数部分接近0.1, 0.2, 0.8, 0.9等适合凑整
        return decimal_part <= 0.3 or decimal_part >= 0.7
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建凑整加法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 确定哪个数适合凑整
        if self._can_round_to_integer(a):
            target_num, other_num = a, b
            target_name, other_name = "第一个数", "第二个数"
        else:
            target_num, other_num = b, a
            target_name, other_name = "第二个数", "第一个数"
        
        # 计算调整量
        decimal_part = target_num - int(target_num)
        # 调整float精度问题
        decimal_part = round(decimal_part, 10)
        if decimal_part <= 0.5:
            # 向上凑整
            adjustment = 1 - decimal_part
            rounded_num = int(target_num) + 1
            operation_desc = "向上凑整"
        else:
            # 向下凑整
            adjustment = decimal_part
            rounded_num = int(target_num)
            operation_desc = "向下凑整"
        
        steps.append(CalculationStep(
            description=f"{target_name}{target_num}{operation_desc}到{rounded_num}，调整量为{adjustment}",
            operation="确定凑整策略",
            result=f"调整量：{adjustment}"
        ))
        
        # 执行凑整计算
        if decimal_part <= 0.5:
            # 向上凑整：(a + 调整) + (b - 调整)
            temp_result = rounded_num + other_num
            steps.append(CalculationStep(
                description=f"先算：{rounded_num} + {other_num} = {temp_result}",
                operation="凑整后相加",
                result=temp_result
            ))
            
            final_result = temp_result - adjustment
            steps.append(CalculationStep(
                description=f"减去调整量：{temp_result} - {adjustment} = {final_result}",
                operation="还原调整",
                result=final_result,
                formula="凑整法：(数1+调整) + (数2-调整) = 结果"
            ))
        else:
            # 向下凑整：(a - 调整) + (b + 调整)
            temp_result = rounded_num + other_num
            steps.append(CalculationStep(
                description=f"先算：{rounded_num} + {other_num} = {temp_result}",
                operation="凑整后相加",
                result=temp_result
            ))
            
            final_result = temp_result + adjustment
            steps.append(CalculationStep(
                description=f"加上调整量：{temp_result} + {adjustment} = {final_result}",
                operation="还原调整",
                result=final_result,
                formula="凑整法：(数1-调整) + (数2+调整) = 结果"
            ))
        
        return steps
