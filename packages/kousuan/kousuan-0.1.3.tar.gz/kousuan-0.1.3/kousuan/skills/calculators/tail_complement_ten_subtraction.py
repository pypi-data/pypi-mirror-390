"""
尾数凑十减法实现
处理个位不够减时通过凑十简化计算的减法，如52-28=24
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class TailComplementTenSubtraction(MathCalculator):
    """尾数凑十减法算法"""
    
    def __init__(self):
        super().__init__("尾数凑十减法", "个位不够减时通过凑十简化计算", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：个位不够减，且减数个位接近10的情况"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 两位数减法
            if not (10 <= minuend <= 99 and 10 <= subtrahend <= 99):
                return False
            
            minuend_ones = minuend % 10
            subtrahend_ones = subtrahend % 10
            
            # 个位不够减，且减数个位≥6（接近10）
            return (minuend_ones < subtrahend_ones and subtrahend_ones >= 6)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建尾数凑十减法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        minuend_tens = minuend // 10
        minuend_ones = minuend % 10
        subtrahend_tens = subtrahend // 10
        subtrahend_ones = subtrahend % 10
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用尾数凑十减法",
            operation="识别凑十机会",
            result=f"个位{minuend_ones}不够减{subtrahend_ones}，使用凑十法"
        ))
        
        # 将减数凑到整十数
        round_subtrahend = subtrahend_tens * 10 + 10  # 凑到下一个整十数
        complement = round_subtrahend - subtrahend
        
        steps.append(CalculationStep(
            description=f"将{subtrahend}凑整到{round_subtrahend}，需要加{complement}",
            operation="确定凑整数",
            result=f"{subtrahend} → {round_subtrahend}"
        ))
        
        # 先减去凑整后的数
        temp_result = minuend - round_subtrahend
        steps.append(CalculationStep(
            description=f"先算：{minuend} - {round_subtrahend} = {temp_result}",
            operation="减去凑整数",
            result=temp_result
        ))
        
        # 加回多减的部分
        final_result = temp_result + complement
        steps.append(CalculationStep(
            description=f"多减了{complement}，需要加回：{temp_result} + {complement} = {final_result}",
            operation="加回多减部分",
            result=final_result,
            formula="尾数凑十减法：先减整十数，再加回差值"
        ))
        
        return steps