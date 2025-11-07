"""
整数倍数除法实现
处理整倍数的除法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class IntegerMultipleDivision(MathCalculator):
    """整数倍数除法算法"""
    
    def __init__(self):
        super().__init__("整数倍数除法", "整倍数，直接商", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被除数是除数的整数倍，但不能被其他专门算法处理"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(dividend, int) and isinstance(divisor, int)):
                return False
            
            if divisor == 0:
                return False
            
            # 必须是整除关系
            if dividend % divisor != 0:
                return False
            
            quotient = dividend // divisor
            
            # 排除九九表范围（让九九表算法优先处理）
            if (dividend <= 144 and 1 <= divisor <= 12 and 1 <= quotient <= 12):
                return False
            
            # 排除整十数除法（让整十除法算法优先处理）
            if (dividend % 10 == 0 and divisor % 10 == 0 and divisor >= 10):
                return False
            
            # 除数不能是1（太简单，让通用算法处理）
            if divisor == 1:
                return False
            
            # 被除数和除数都应该在合理范围内
            if dividend > 9999 or divisor > 999:
                return False
            
            # 商应该是简单的整数（2-99）
            return 2 <= quotient <= 99
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建整数倍数除法步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        # 确保是整数
        dividend_int = int(dividend)
        divisor_int = int(divisor)
        
        quotient = dividend_int // divisor_int
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别整数倍数除法：{dividend_int} ÷ {divisor_int}",
            operation="识别模式",
            result="整倍数，直接商"
        ))
        
        # 验证是否整除
        steps.append(CalculationStep(
            description=f"验证整倍关系：{dividend_int} ÷ {divisor_int}",
            operation="整除验证",
            result=f"{dividend_int} 是 {divisor_int} 的整数倍"
        ))
        
        # 展示倍数关系
        steps.append(CalculationStep(
            description=f"倍数关系：{divisor_int} × {quotient} = {dividend_int}",
            operation="建立关系",
            result=f"{dividend_int} 是 {divisor_int} 的 {quotient} 倍"
        ))
        
        # 直接给出商
        steps.append(CalculationStep(
            description=f"直接得出商：{dividend_int} ÷ {divisor_int} = {quotient}",
            operation="得出答案",
            result=quotient,
            formula="整数倍除法：k × n ÷ n = k"
        ))
        
        # 如果商是特殊数字，给出额外提示
        if quotient in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            steps.append(CalculationStep(
                description=f"记忆技巧：{divisor_int} 的 {quotient} 倍就是 {dividend_int}",
                operation="记忆提示",
                result=f"可以记住 {quotient} × {divisor_int} = {dividend_int}"
            ))
        elif quotient % 10 == 0:  # 整十倍数
            steps.append(CalculationStep(
                description=f"整十倍数：{divisor_int} 的 {quotient} 倍",
                operation="特殊倍数",
                result=f"{quotient//10}个十倍 = {quotient}倍"
            ))
        
        return steps