"""
近整百减法实现
处理接近整百数的减法，如207-198=9
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class NearHundredSubtraction(MathCalculator):
    """近整百减法算法"""
    
    def __init__(self):
        super().__init__("近整百减法", "处理接近整百数的减法", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被减数和减数都接近整百数"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 三位数且都接近整百数
            if not (100 <= minuend <= 999 and 100 <= subtrahend <= 999):
                return False
            
            # 检查是否都接近整百数（与最近整百数的差距小于等于10）
            minuend_hundred = round(minuend / 100) * 100
            subtrahend_hundred = round(subtrahend / 100) * 100
            
            minuend_diff = abs(minuend - minuend_hundred)
            subtrahend_diff = abs(subtrahend - subtrahend_hundred)
            
            # 都接近整百数
            return minuend_diff <= 10 and subtrahend_diff <= 10
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建近整百减法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用近整百减法",
            operation="识别近整百数",
            result="被减数和减数都接近整百数"
        ))
        
        # 找到最近的整百数
        minuend_hundred = round(minuend / 100) * 100
        subtrahend_hundred = round(subtrahend / 100) * 100
        
        # 计算与整百数的差值
        minuend_diff = minuend - minuend_hundred
        subtrahend_diff = subtrahend - subtrahend_hundred
        
        steps.append(CalculationStep(
            description=f"分解为整百数部分：{minuend} = {minuend_hundred} + ({minuend_diff}), {subtrahend} = {subtrahend_hundred} + ({subtrahend_diff})",
            operation="分解整百数",
            result=f"整百数部分：{minuend_hundred} - {subtrahend_hundred}"
        ))
        
        # 先计算整百数部分
        hundred_result = minuend_hundred - subtrahend_hundred
        steps.append(CalculationStep(
            description=f"整百数相减：{minuend_hundred} - {subtrahend_hundred} = {hundred_result}",
            operation="计算整百数差",
            result=hundred_result
        ))
        
        # 计算余数部分
        remainder_diff = minuend_diff - subtrahend_diff
        steps.append(CalculationStep(
            description=f"余数相减：({minuend_diff}) - ({subtrahend_diff}) = {remainder_diff}",
            operation="计算余数差",
            result=remainder_diff
        ))
        
        # 最终结果
        final_result = hundred_result + remainder_diff
        steps.append(CalculationStep(
            description=f"组合结果：{hundred_result} + ({remainder_diff}) = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="近整百减法：(100a+x) - (100b+y) = 100(a-b) + (x-y)"
        ))
        
        return steps