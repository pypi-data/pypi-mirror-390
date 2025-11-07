"""
除以9实现
利用9的特殊性质进行快速计算
包括数字根方法和分拆方法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class DivideByNine(MathCalculator):
    """除以9算法"""
    
    def __init__(self):
        super().__init__("除9速算", "九分法，看数根", priority=6)
    
    def _digital_root(self, num: int) -> int:
        """计算数字根（各位数字之和的最终值）"""
        while num >= 10:
            num = sum(int(digit) for digit in str(num))
        return num
    
    def _sum_of_digits(self, num: int) -> int:
        """计算各位数字之和"""
        return sum(int(digit) for digit in str(num))
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数除以9"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            return isinstance(divisor, (int, float)) and divisor == 9
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建除以9速算步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 确保被除数是整数
        if isinstance(dividend, float) and dividend.is_integer():
            dividend = int(dividend)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ 9 使用除9速算法",
            operation="识别除以9",
            result="九分法，看数根"
        ))
        
        if isinstance(dividend, int):
            # 方法1：检查是否能被9整除（数字根判断法）
            digit_sum = self._sum_of_digits(dividend)
            digital_root = self._digital_root(dividend)
            
            steps.append(CalculationStep(
                description=f"计算各位数字之和：{dividend} → {' + '.join(str(dividend))} = {digit_sum}",
                operation="数字和",
                result=digit_sum
            ))
            
            if digit_sum != digital_root:
                steps.append(CalculationStep(
                    description=f"继续求和直到个位数：{digit_sum} → {digital_root}",
                    operation="数字根",
                    result=f"数字根是 {digital_root}"
                ))
            
            if digital_root == 9 or dividend % 9 == 0:
                # 能被9整除
                quotient = dividend // 9
                steps.append(CalculationStep(
                    description=f"数字根是9（或各位数字和能被9整除），所以{dividend}能被9整除",
                    operation="整除判断",
                    result=f"{dividend} ÷ 9 = {quotient}"
                ))
                
                # 提供验证方法
                if dividend <= 999:
                    # 对于小数字，提供心算技巧
                    steps.append(CalculationStep(
                        description=f"心算技巧：想9的多少倍接近{dividend}",
                        operation="心算技巧",
                        result=f"9 × {quotient} = {9 * quotient}"
                    ))
                
                final_result = quotient
            else:
                # 不能被9整除
                quotient = dividend // 9
                remainder = dividend % 9
                
                steps.append(CalculationStep(
                    description=f"数字根不是9，说明不能整除，有余数",
                    operation="有余数",
                    result=f"商 {quotient}，余数 {remainder}"
                ))
                
                final_result = dividend / 9
                
                steps.append(CalculationStep(
                    description=f"小数形式：{dividend} ÷ 9 = {final_result}",
                    operation="小数结果",
                    result=final_result
                ))
            
            # 对于特殊情况，提供分拆方法
            if dividend >= 18 and dividend <= 999:
                # 寻找便于计算的分拆方式
                if dividend >= 90:
                    # 分拆为90的倍数加余数
                    ninety_multiple = (dividend // 90) * 90
                    remainder_part = dividend - ninety_multiple
                    
                    if ninety_multiple > 0:
                        steps.append(CalculationStep(
                            description=f"分拆法：{dividend} = {ninety_multiple} + {remainder_part}",
                            operation="分拆方法",
                            result=f"{ninety_multiple} ÷ 9 + {remainder_part} ÷ 9 = {ninety_multiple//9} + {remainder_part/9}"
                        ))
        else:
            # 浮点数除法
            final_result = dividend / 9
            steps.append(CalculationStep(
                description=f"小数除法：{dividend} ÷ 9 = {final_result}",
                operation="小数计算",
                result=final_result
            ))
        
        # 确保final_result已定义
        if 'final_result' not in locals():
            final_result = dividend / 9
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ 9 = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="除以9：数字根判断 + 心算技巧"
        ))
        
        return steps