"""
首数估商法实现
在长除法中，只看被除数和除数的首位（或前两位）来快速估算商的第一位
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class FirstDigitEstimateDivision(MathCalculator):
    """首数估商法算法"""
    
    def __init__(self):
        super().__init__("首数估商法", "看首位，估商数", priority=4)
    
    def _get_first_digits(self, num, count: int = 2) -> int:
        """获取数字的前几位"""
        str_num = str(int(num))
        if len(str_num) <= count:
            return int(str_num)
        return int(str_num[:count])
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：多位数除法，适合首位估算"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            
            if not (isinstance(dividend, (int, float)) and isinstance(divisor, (int, float))):
                return False
            
            if divisor == 0:
                return False
            
            # 被除数必须是多位数（至少3位）
            if dividend < 100:
                return False
            
            # 除数应该是1-2位数，便于心算
            if divisor >= 100 or divisor < 2:
                return False
            
            # 商应该是多位数，这样首数估商才有意义
            quotient = dividend / divisor
            if quotient < 10:
                return False
            
            return True
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建首数估商法步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 确保是整数
        dividend_int = int(dividend)
        divisor_int = int(divisor)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend_int} ÷ {divisor_int} 使用首数估商法",
            operation="识别多位除法",
            result="看首位，估商数"
        ))
        
        # 分析被除数和除数的位数
        dividend_str = str(dividend_int)
        divisor_str = str(divisor_int)
        dividend_digits = len(dividend_str)
        divisor_digits = len(divisor_str)
        
        steps.append(CalculationStep(
            description=f"被除数{dividend_int}是{dividend_digits}位数，除数{divisor_int}是{divisor_digits}位数",
            operation="分析位数",
            result=f"商大约是{dividend_digits - divisor_digits + 1}位数"
        ))
        
        # 首数估算
        if divisor_digits == 1:
            # 除数是一位数
            dividend_first = int(dividend_str[0])
            if dividend_first >= divisor_int:
                first_quotient = dividend_first // divisor_int
                steps.append(CalculationStep(
                    description=f"首位估商：{dividend_first} ÷ {divisor_int} ≈ {first_quotient}",
                    operation="首位估算",
                    result=f"商的首位大约是{first_quotient}"
                ))
            else:
                # 需要看前两位
                dividend_first_two = int(dividend_str[:2])
                first_quotient = dividend_first_two // divisor_int
                steps.append(CalculationStep(
                    description=f"首位不够，看前两位：{dividend_first_two} ÷ {divisor_int} ≈ {first_quotient}",
                    operation="前两位估算",
                    result=f"商的首位大约是{first_quotient}"
                ))
        else:
            # 除数是两位数
            dividend_first_n = self._get_first_digits(dividend_int, divisor_digits + 1)
            divisor_first_n = self._get_first_digits(divisor_int, divisor_digits)
            
            first_quotient = dividend_first_n // divisor_first_n
            
            steps.append(CalculationStep(
                description=f"首数估商：{dividend_first_n} ÷ {divisor_first_n} ≈ {first_quotient}",
                operation="首数估算",
                result=f"商的首位大约是{first_quotient}"
            ))
        
        # 验证估算并调整
        estimated_product = first_quotient * divisor_int
        
        # 根据位数确定估算商的量级
        expected_digits = dividend_digits - divisor_digits + 1
        if expected_digits > 1:
            estimated_quotient = first_quotient * (10 ** (expected_digits - 1))
            estimated_product = estimated_quotient * divisor_int
            
            steps.append(CalculationStep(
                description=f"估算完整商：约{estimated_quotient}，验证：{estimated_quotient} × {divisor_int} = {estimated_product}",
                operation="估算验证",
                result=f"估算商接近{estimated_quotient}"
            ))
        
        # 计算精确结果
        actual_quotient = dividend_int / divisor_int
        
        if isinstance(actual_quotient, float) and actual_quotient.is_integer():
            actual_quotient = int(actual_quotient)
        
        # 比较估算和实际结果
        if isinstance(actual_quotient, int):
            actual_str = str(actual_quotient)
            estimated_first = str(first_quotient)[0]
            actual_first = actual_str[0]
            
            if estimated_first == actual_first:
                steps.append(CalculationStep(
                    description=f"估算准确！实际商：{actual_quotient}，首位确实是{actual_first}",
                    operation="估算成功",
                    result="✓ 首位估算正确"
                ))
            else:
                steps.append(CalculationStep(
                    description=f"估算偏差：实际商{actual_quotient}，首位是{actual_first}而不是{estimated_first}",
                    operation="估算调整",
                    result=f"需要微调估算"
                ))
        
        steps.append(CalculationStep(
            description=f"精确结果：{dividend_int} ÷ {divisor_int} = {actual_quotient}",
            operation="精确计算",
            result=actual_quotient,
            formula="首数估商法：先估首位，后精算"
        ))
        
        # 提供心算技巧
        if divisor_int <= 12:
            steps.append(CalculationStep(
                description=f"心算技巧：熟记{divisor_int}的倍数表，快速确定商的范围",
                operation="心算提示",
                result=f"{divisor_int}的倍数：{divisor_int}×10={divisor_int*10}, {divisor_int}×100={divisor_int*100}"
            ))
        
        return steps