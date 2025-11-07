"""
通用除法实现
作为兜底算法处理所有其他除法情况
"""

from typing import List, Union
from decimal import Decimal, getcontext
from fractions import Fraction
from ..base_types import MathCalculator, Formula, CalculationStep

# 设置小数精度
getcontext().prec = 28


class GeneralDivision(MathCalculator):
    """通用除法算法"""
    
    def __init__(self):
        super().__init__("通用除法", "化分简，心算快", priority=1)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：所有除法运算（最低优先级，兜底算法）"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if divisor == 0:
                return False
            # 支持整数、浮点数
            return isinstance(dividend, (int, float)) and isinstance(divisor, (int, float))
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建通用除法步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 转换Fraction为float以便处理
        if isinstance(dividend, Fraction):
            dividend = float(dividend)
        if isinstance(divisor, Fraction):
            divisor = float(divisor)
        
        # 检查特殊情况
        if divisor == 0:
            return self._construct_zero_division_steps(dividend, divisor)
        elif dividend == 0:
            return self._construct_zero_dividend_steps(dividend, divisor)
        elif divisor == 1:
            return self._construct_one_division_steps(dividend, divisor)
        elif isinstance(dividend, float) or isinstance(divisor, float):
            return self._construct_decimal_steps(dividend, divisor)
        elif dividend < 0 or divisor < 0:
            return self._construct_negative_steps(dividend, divisor)
        else:
            return self._construct_general_steps(int(dividend), int(divisor))
    
    def _construct_zero_division_steps(self, dividend: Union[int, float], divisor: Union[int, float]) -> List[CalculationStep]:
        """构建被零除的错误步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 检测到除零错误",
            operation="检测除零",
            result="任何数都不能被零除"
        ))
        
        steps.append(CalculationStep(
            description="除零操作是未定义的数学运算",
            operation="数学规则",
            result="错误：除数不能为零",
            formula="a ÷ 0 = 未定义"
        ))
        
        return steps
    
    def _construct_zero_dividend_steps(self, dividend: Union[int, float], divisor: Union[int, float]) -> List[CalculationStep]:
        """构建零被除的步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 识别零被除规律",
            operation="识别零被除",
            result="零被任何非零数除都等于零"
        ))
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} = 0",
            operation="应用零被除规律",
            result=0,
            formula="0 ÷ a = 0 (a ≠ 0)"
        ))
        
        return steps
    
    def _construct_one_division_steps(self, dividend: Union[int, float], divisor: Union[int, float]) -> List[CalculationStep]:
        """构建被1除的步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 识别被1除规律",
            operation="识别被1除",
            result="任何数被1除都等于原数"
        ))
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} = {dividend}",
            operation="应用被1除规律",
            result=dividend,
            formula="a ÷ 1 = a"
        ))
        
        return steps
    
    def _construct_negative_steps(self, dividend: Union[int, float], divisor: Union[int, float]) -> List[CalculationStep]:
        """构建负数除法步骤"""
        steps = []
        
        # 判断符号
        is_dividend_negative = dividend < 0
        is_divisor_negative = divisor < 0
        result_positive = not (is_dividend_negative ^ is_divisor_negative)  # 异或取反
        
        abs_dividend = abs(dividend)
        abs_divisor = abs(divisor)
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 处理负数除法",
            operation="分析符号",
            result="负数除法：同号为正，异号为负"
        ))
        
        steps.append(CalculationStep(
            description=f"符号分析：{dividend} {'< 0' if is_dividend_negative else '> 0'}, {divisor} {'< 0' if is_divisor_negative else '> 0'}",
            operation="确定结果符号",
            result=f"结果为{'正数' if result_positive else '负数'}"
        ))
        
        steps.append(CalculationStep(
            description=f"取绝对值：|{dividend}| = {abs_dividend}, |{divisor}| = {abs_divisor}",
            operation="计算绝对值",
            result=f"计算 {abs_dividend} ÷ {abs_divisor}"
        ))
        
        # 递归处理绝对值除法
        abs_result = abs_dividend / abs_divisor
        
        steps.append(CalculationStep(
            description=f"{abs_dividend} ÷ {abs_divisor} = {abs_result}",
            operation="计算绝对值商",
            result=abs_result
        ))
        
        final_result = abs_result if result_positive else -abs_result
        steps.append(CalculationStep(
            description=f"添加符号：{abs_result} → {final_result}",
            operation="确定最终结果",
            result=final_result,
            formula="负数除法：(-a) ÷ (-b) = ab, (-a) ÷ b = -a/b"
        ))
        
        return steps
    
    def _construct_decimal_steps(self, dividend: Union[int, float], divisor: Union[int, float]) -> List[CalculationStep]:
        """构建小数除法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 处理小数除法",
            operation="识别小数",
            result="小数除法：转换为分数或整数计算"
        ))
        
        # 计算结果
        result = dividend / divisor
        
        # 检查是否能转换为简单分数
        try:
            # 尝试将结果转换为分数
            fraction_result = Fraction(result).limit_denominator(100)
            if abs(float(fraction_result) - result) < 0.001 and fraction_result.denominator <= 20:
                steps.append(CalculationStep(
                    description=f"{dividend} ÷ {divisor} = {fraction_result}",
                    operation="分数形式",
                    result=f"分数形式：{fraction_result}"
                ))
                
                # 如果是假分数且能化为带分数
                if fraction_result > 1:
                    whole = fraction_result.numerator // fraction_result.denominator
                    remainder = fraction_result.numerator % fraction_result.denominator
                    if remainder > 0:
                        steps.append(CalculationStep(
                            description=f"化为带分数：{whole} 又 {remainder}/{fraction_result.denominator}",
                            operation="带分数形式",
                            result=f"带分数：{whole} {remainder}/{fraction_result.denominator}"
                        ))
        except:
            pass
        
        steps.append(CalculationStep(
            description=f"小数结果：{dividend} ÷ {divisor} = {result}",
            operation="小数计算",
            result=result,
            formula="小数除法：直接计算或化为分数"
        ))
        
        return steps
    
    def _construct_general_steps(self, dividend: int, divisor: int) -> List[CalculationStep]:
        """构建一般整数除法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 使用长除法",
            operation="识别一般除法",
            result="按照长除法步骤计算"
        ))
        
        result = dividend / divisor
        quotient = dividend // divisor
        remainder = dividend % divisor
        
        if remainder == 0:
            # 整除情况
            steps.append(CalculationStep(
                description=f"{dividend} ÷ {divisor} = {quotient}",
                operation="整除计算",
                result=quotient,
                formula="整除：被除数 = 除数 × 商"
            ))
            
            steps.append(CalculationStep(
                description=f"验证：{divisor} × {quotient} = {dividend}",
                operation="验证结果",
                result="✓ 计算正确"
            ))
        else:
            # 有余数情况
            steps.append(CalculationStep(
                description=f"{dividend} ÷ {divisor} = {quotient} 余 {remainder}",
                operation="带余除法",
                result=f"商 {quotient}，余数 {remainder}"
            ))
            
            # 转换为小数形式
            steps.append(CalculationStep(
                description=f"小数形式：{dividend} ÷ {divisor} = {result}",
                operation="小数表示",
                result=result,
                formula="带余除法：被除数 = 除数 × 商 + 余数"
            ))
            
            # 如果可以，提供分数形式
            try:
                fraction = Fraction(dividend, divisor)
                if fraction.denominator <= 20:
                    steps.append(CalculationStep(
                        description=f"分数形式：{dividend} ÷ {divisor} = {fraction}",
                        operation="分数表示",
                        result=f"分数：{fraction}"
                    ))
            except:
                pass
        
        return steps