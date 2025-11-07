"""
除以125实现
利用125 = 1000/8的特点，转换为乘以8再除以1000
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class DivideByOneHundredTwentyFive(MathCalculator):
    """除以125算法"""
    
    def __init__(self):
        super().__init__("除125速算", "除以125转换为乘8除1000", priority=6)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数除以125"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not isinstance(divisor, (int, float)):
                return False
            
            # 检查是否是除以125
            return divisor == 125
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建除125速算步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ 125 使用除125速算法",
            operation="识别模式",
            result="125 = 1000 ÷ 8，转换为乘8除1000"
        ))
        
        # 乘以8
        product = dividend * 8
        steps.append(CalculationStep(
            description=f"{dividend} × 8 = {product}",
            operation="乘以8",
            result=product
        ))
        
        # 除以1000
        if isinstance(product, int) and product % 1000 == 0:
            final_result = product // 1000
            steps.append(CalculationStep(
                description=f"{product} ÷ 1000 = {final_result}",
                operation="除以1000",
                result=final_result
            ))
        else:
            final_result = product / 1000
            
            # 处理小数点移位的详细说明
            if isinstance(product, int):
                product_str = str(product)
                if len(product_str) >= 3:
                    # 有足够位数，直接移动小数点
                    integer_part = product_str[:-3]
                    decimal_part = product_str[-3:]
                    if integer_part == '':
                        result_str = '0.' + decimal_part
                    else:
                        result_str = integer_part + '.' + decimal_part
                    
                    # 去掉末尾的零
                    if '.' in result_str:
                        result_str = result_str.rstrip('0').rstrip('.')
                    
                    steps.append(CalculationStep(
                        description=f"{product} ÷ 1000 = {result_str}（小数点左移3位）",
                        operation="小数点移位",
                        result=result_str
                    ))
                else:
                    # 位数不足，需要补零
                    zeros_needed = 3 - len(product_str)
                    result_str = '0.' + '0' * zeros_needed + product_str
                    
                    steps.append(CalculationStep(
                        description=f"{product} ÷ 1000 = {result_str}（位数不足，前补零）",
                        operation="补零移位",
                        result=result_str
                    ))
            else:
                steps.append(CalculationStep(
                    description=f"{product} ÷ 1000 = {final_result}",
                    operation="除以1000",
                    result=final_result
                ))
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ 125 = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="a ÷ 125 = (a × 8) ÷ 1000"
        ))
        
        # 提供验证
        verification = final_result * 125
        if abs(verification - dividend) < 0.001:
            steps.append(CalculationStep(
                description=f"验证：{final_result} × 125 = {verification}",
                operation="验证正确",
                result="✓ 计算正确"
            ))
        
        return steps