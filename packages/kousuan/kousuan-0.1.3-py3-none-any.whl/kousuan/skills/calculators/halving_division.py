"""
减半法除法实现
除以2就是将一个数对半分
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class HalvingDivision(MathCalculator):
    """减半法除法算法"""
    
    def __init__(self):
        super().__init__("减半法", "除以2就是对半分", priority=7)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任何数除以2"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            return isinstance(divisor, (int, float)) and divisor == 2
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建减半法除法步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ 2 使用减半法",
            operation="识别除以2",
            result="除以2就是对半分"
        ))
        
        if isinstance(dividend, int):
            if dividend % 2 == 0:
                # 偶数，可以整除
                result = dividend // 2
                steps.append(CalculationStep(
                    description=f"{dividend} 是偶数，对半分得 {result}",
                    operation="偶数减半",
                    result=result
                ))
            else:
                # 奇数，结果是小数
                result = dividend / 2
                whole_part = dividend // 2
                steps.append(CalculationStep(
                    description=f"{dividend} 是奇数，{dividend} = {whole_part} × 2 + 1",
                    operation="奇数分析",
                    result=f"商 {whole_part} 余 1"
                ))
                
                steps.append(CalculationStep(
                    description=f"余数1除以2等于0.5，所以 {dividend} ÷ 2 = {whole_part} + 0.5 = {result}",
                    operation="处理余数",
                    result=result
                ))
        else:
            # 浮点数
            result = dividend / 2
            steps.append(CalculationStep(
                description=f"小数减半：{dividend} ÷ 2 = {result}",
                operation="小数减半",
                result=result
            ))
        
        # 提供心算技巧
        if isinstance(dividend, int) and dividend >= 10:
            if dividend < 100:
                # 两位数的心算技巧
                tens = dividend // 10
                ones = dividend % 10
                
                if ones % 2 == 0:
                    # 个位是偶数
                    steps.append(CalculationStep(
                        description=f"心算技巧：{dividend} = {tens}0 + {ones}，分别减半再相加",
                        operation="分位减半",
                        result=f"{tens}0 ÷ 2 + {ones} ÷ 2 = {tens*10//2} + {ones//2} = {tens*10//2 + ones//2}"
                    ))
                else:
                    # 个位是奇数
                    steps.append(CalculationStep(
                        description=f"心算技巧：{dividend} = {tens}0 + {ones}，{tens}0 ÷ 2 = {tens*5}，{ones} ÷ 2 = {ones/2}",
                        operation="分位减半",
                        result=f"{tens*5} + {ones/2} = {tens*5 + ones/2}"
                    ))
        
        final_result = dividend / 2
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ 2 = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="减半法：a ÷ 2 = a/2"
        ))
        
        return steps