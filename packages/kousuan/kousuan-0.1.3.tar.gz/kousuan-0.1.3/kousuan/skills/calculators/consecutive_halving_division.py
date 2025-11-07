"""
连续减半法除法实现
除以4等于连续减半两次；除以8等于连续减半三次
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ConsecutiveHalvingDivision(MathCalculator):
    """连续减半法除法算法"""
    
    def __init__(self):
        super().__init__("连续减半法", "除以4、8等2的幂，连续减半", priority=7)
    
    def _is_power_of_two(self, num: int) -> bool:
        """检查是否为2的幂"""
        if num <= 0:
            return False
        return (num & (num - 1)) == 0
    
    def _get_power_of_two(self, num: int) -> int:
        """获取2的幂次"""
        if not self._is_power_of_two(num):
            return 0
        power = 0
        while num > 1:
            num //= 2
            power += 1
        return power
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：除数是2的幂（4, 8, 16, 32...）"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not isinstance(divisor, (int, float)):
                return False
            
            # 除数必须是2的幂，且大于2（排除除以2的情况，让减半法处理）
            if isinstance(divisor, float):
                if divisor.is_integer():
                    divisor = int(divisor)
                else:
                    return False
            
            return divisor > 2 and self._is_power_of_two(divisor)
            
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建连续减半法除法步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 确保除数是整数
        if isinstance(divisor, float) and divisor.is_integer():
            divisor = int(divisor)
        
        power = self._get_power_of_two(int(divisor))
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 使用连续减半法",
            operation="识别2的幂",
            result=f"{divisor} = 2^{power}，需要连续减半{power}次"
        ))
        
        # 逐步减半
        current_value = dividend
        
        for i in range(power):
            next_value = current_value / 2
            
            steps.append(CalculationStep(
                description=f"第{i+1}次减半：{current_value} ÷ 2 = {next_value}",
                operation=f"减半{i+1}",
                result=next_value
            ))
            
            current_value = next_value
        
        final_result = current_value
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        # 提供一步法公式
        steps.append(CalculationStep(
            description=f"一步法验证：{dividend} ÷ {divisor} = {final_result}",
            operation="验证结果",
            result=final_result,
            formula=f"除以{divisor}：连续减半{power}次"
        ))
        
        # 提供心算技巧
        if isinstance(dividend, int) and dividend >= 16:
            if divisor == 4:
                steps.append(CalculationStep(
                    description=f"心算技巧：除以4 = 除以2再除以2，或者直接想{divisor}的多少倍是{dividend}",
                    operation="心算提示",
                    result=f"4 × {final_result} = {dividend}"
                ))
            elif divisor == 8:
                steps.append(CalculationStep(
                    description=f"心算技巧：除以8 = 连续3次减半，或者背诵8的倍数表",
                    operation="心算提示",
                    result=f"8 × {final_result} = {dividend}"
                ))
            elif divisor == 16:
                steps.append(CalculationStep(
                    description=f"心算技巧：除以16 = 4次减半，相当于小数点左移4位（对于16进制思维）",
                    operation="心算提示",
                    result=f"16 × {final_result} = {dividend}"
                ))
        
        return steps