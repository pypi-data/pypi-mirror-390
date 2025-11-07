"""
减整补差法实现（前九后十法）
从1000, 10000...中减去一个数
结果的前几位是9减去原数的前几位，最后一位是10减去原数的个位
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class PowerOfTenSubtraction(MathCalculator):
    """减整补差法算法（前九后十法）"""
    
    def __init__(self):
        super().__init__("减整补差法", "从10的幂中减数的特殊技巧（前九后十法）", priority=7)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被减数是10的幂（如100, 1000, 10000）"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 被减数必须是10的幂，且减数小于被减数
            if subtrahend >= minuend or subtrahend <= 0:
                return False
            
            # 检查被减数是否为10的幂
            return self._is_power_of_ten(minuend) and minuend > subtrahend
            
        except:
            return False
    
    def _is_power_of_ten(self, num: int) -> bool:
        """检查是否为10的幂"""
        if num <= 0:
            return False
        
        str_num = str(num)
        return str_num[0] == '1' and all(d == '0' for d in str_num[1:])
    
    def _get_power_info(self, num: int) -> tuple:
        """获取10的幂的信息，返回(指数, 位数)"""
        str_num = str(num)
        power = len(str_num) - 1
        return power, len(str_num)
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建减整补差法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        power, digits = self._get_power_info(minuend)
        subtrahend_str = str(subtrahend).zfill(digits - 1)  # 补齐位数
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用减整补差法（前九后十法）",
            operation="识别10的幂减法",
            result=f"{minuend} = 10^{power}，使用前九后十法"
        ))
        
        steps.append(CalculationStep(
            description=f"将减数补齐位数：{subtrahend} → {subtrahend_str}",
            operation="补齐位数",
            result=f"减数各位：{' '.join(subtrahend_str)}"
        ))
        
        # 应用前九后十法则
        result_digits = []
        process_details = []
        
        # 处理前面的位数（用9减）
        for i in range(len(subtrahend_str) - 1):
            digit = int(subtrahend_str[i])
            result_digit = 9 - digit
            result_digits.append(str(result_digit))
            process_details.append(f"9 - {digit} = {result_digit}")
        
        # 处理最后一位（用10减）
        last_digit = int(subtrahend_str[-1])
        result_last = 10 - last_digit
        if result_last == 10:
            # 需要进位
            result_digits.append("0")
            # 向前进位
            for i in range(len(result_digits) - 2, -1, -1):
                if result_digits[i] == '9':
                    result_digits[i] = '0'
                else:
                    result_digits[i] = str(int(result_digits[i]) + 1)
                    break
            process_details.append(f"10 - {last_digit} = 10 → 0（进位）")
        else:
            result_digits.append(str(result_last))
            process_details.append(f"10 - {last_digit} = {result_last}")
        
        steps.append(CalculationStep(
            description=f"应用前九后十法：{'; '.join(process_details)}",
            operation="前九后十计算",
            result="从左到右依次计算各位"
        ))
        
        # 组合结果
        result_str = ''.join(result_digits)
        final_result = int(result_str)
        
        steps.append(CalculationStep(
            description=f"组合各位数字：{' '.join(result_digits)} = {final_result}",
            operation="组合结果",
            result=final_result,
            formula="前九后十法：10^n - abc... = (9-a)(9-b)...(10-c)"
        ))
        
        return steps