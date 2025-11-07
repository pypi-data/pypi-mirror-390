"""
近整百加法实现
处理接近整百数的加法，如198+207=405
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class NearHundredAddition(MathCalculator):
    """近整百加法算法"""
    
    def __init__(self):
        super().__init__("近整百加法", "处理接近整百数的加法", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个数都接近整百数"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, int) and isinstance(addend2, int)):
                return False
            
            # 三位数且都接近整百数
            if not (100 <= addend1 <= 999 and 100 <= addend2 <= 999):
                return False
            
            # 检查是否都接近整百数（与最近整百数的差距小于等于15）
            addend1_hundred = round(addend1 / 100) * 100
            addend2_hundred = round(addend2 / 100) * 100
            
            addend1_diff = abs(addend1 - addend1_hundred)
            addend2_diff = abs(addend2 - addend2_hundred)
            
            # 都接近整百数
            return addend1_diff <= 15 and addend2_diff <= 15
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建近整百加法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用近整百加法",
            operation="识别近整百数",
            result="两个加数都接近整百数"
        ))
        
        # 找到最近的整百数
        addend1_hundred = round(addend1 / 100) * 100
        addend2_hundred = round(addend2 / 100) * 100
        
        # 计算与整百数的差值
        addend1_diff = addend1 - addend1_hundred
        addend2_diff = addend2 - addend2_hundred
        
        steps.append(CalculationStep(
            description=f"分解为整百数部分：{addend1} = {addend1_hundred} + ({addend1_diff}), {addend2} = {addend2_hundred} + ({addend2_diff})",
            operation="分解整百数",
            result=f"整百数部分：{addend1_hundred} + {addend2_hundred}"
        ))
        
        # 先计算整百数部分
        hundred_sum = addend1_hundred + addend2_hundred
        steps.append(CalculationStep(
            description=f"整百数相加：{addend1_hundred} + {addend2_hundred} = {hundred_sum}",
            operation="计算整百数和",
            result=hundred_sum
        ))
        
        # 计算余数部分
        remainder_sum = addend1_diff + addend2_diff
        steps.append(CalculationStep(
            description=f"余数相加：({addend1_diff}) + ({addend2_diff}) = {remainder_sum}",
            operation="计算余数和",
            result=remainder_sum
        ))
        
        # 最终结果
        final_result = hundred_sum + remainder_sum
        steps.append(CalculationStep(
            description=f"组合结果：{hundred_sum} + ({remainder_sum}) = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="近整百加法：(100a+x) + (100b+y) = 100(a+b) + (x+y)"
        ))
        
        return steps