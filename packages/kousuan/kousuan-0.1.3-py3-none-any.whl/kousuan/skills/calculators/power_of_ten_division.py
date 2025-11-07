"""
补零法除法实现（除以10的幂）
除以10, 100, 1000等，只需将被除数的小数点向左移动相应位数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class PowerOfTenDivision(MathCalculator):
    """补零法除法算法（除以10的幂）"""
    
    def __init__(self):
        super().__init__("补零法除法", "除以10的幂，小数点左移", priority=8)
    
    def _is_power_of_ten(self, num: int) -> bool:
        """检查是否为10的幂"""
        if num <= 0:
            return False
        
        str_num = str(num)
        return str_num[0] == '1' and all(d == '0' for d in str_num[1:])
    
    def _get_power_of_ten(self, num: int) -> int:
        """获取10的幂次"""
        if not self._is_power_of_ten(num):
            return 0
        return len(str(num)) - 1
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：除数是10的幂（10, 100, 1000...）"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not isinstance(divisor, (int, float)):
                return False
            
            # 除数必须是10的幂
            if isinstance(divisor, float):
                # 处理10.0这样的浮点数
                if divisor.is_integer():
                    divisor = int(divisor)
                else:
                    return False
            
            return self._is_power_of_ten(divisor)
            
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建补零法除法步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 确保除数是整数
        if isinstance(divisor, float) and divisor.is_integer():
            divisor = int(divisor)
        
        power = self._get_power_of_ten(divisor)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 使用补零法除法",
            operation="识别10的幂",
            result=f"{divisor} = 10^{power}，小数点左移{power}位"
        ))
        
        steps.append(CalculationStep(
            description=f"除以10^{power}等于小数点向左移动{power}位",
            operation="规律说明",
            result="补零法：除以10的幂 = 小数点左移"
        ))
        
        # 处理被除数
        if isinstance(dividend, int):
            dividend_str = str(dividend)
            if len(dividend_str) > power:
                # 整数位足够，直接移动小数点
                integer_part = dividend_str[:-power] if power > 0 else dividend_str
                decimal_part = dividend_str[-power:] if power > 0 else ''
                
                if power == 0:
                    result_str = dividend_str
                elif integer_part == '':
                    result_str = '0.' + '0' * (power - len(dividend_str)) + dividend_str
                else:
                    result_str = integer_part + ('.' + decimal_part if decimal_part else '')
                
                steps.append(CalculationStep(
                    description=f"移动小数点：{dividend_str} → {result_str}",
                    operation="小数点移动",
                    result=result_str
                ))
            else:
                # 需要在前面补0
                zeros_needed = power - len(dividend_str)
                result_str = '0.' + '0' * zeros_needed + dividend_str
                
                steps.append(CalculationStep(
                    description=f"位数不足，前面补零：{dividend_str} → {result_str}",
                    operation="补零移位",
                    result=result_str
                ))
        else:
            # 被除数是小数
            result = dividend / divisor
            steps.append(CalculationStep(
                description=f"小数除法：{dividend} ÷ {divisor} = {result}",
                operation="小数计算",
                result=result
            ))
        
        # 计算最终结果
        final_result = dividend / divisor
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ {divisor} = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="a ÷ 10^n = a × 10^(-n)"
        ))
        
        return steps