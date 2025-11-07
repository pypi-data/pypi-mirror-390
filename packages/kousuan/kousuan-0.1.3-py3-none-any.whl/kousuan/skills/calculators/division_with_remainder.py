"""
带余数除法速算算子
匹配带有“······”余数符号的除法题型
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep
import re

class DivisionWithRemainder(MathCalculator):
    def __init__(self):
        super().__init__("带余数除法", "速算带余数的除法题型", priority=2)

    def is_match_pattern(self, formula: Formula) -> bool:
        expr = formula.original_expression
        # 1. 带余数除法题型
        if formula.type == "division" and ("······" in expr or (formula.answer and "······" in str(formula.answer))):
            return True
        # 2. 逆运算最大估值题型（@×8>49/@÷8>49等）
        if "@" in expr and re.search(r'[><=]?', expr):
            return True
        return False

    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        expr = formula.original_expression.replace(' ', '')
        # 1. 逆运算：@÷8=5······4 形式
        match = re.match(r'@÷(\d+)=([\d]+)······([\d]+)', expr)
        if match:
            divisor = int(match.group(1))
            quotient = int(match.group(2))
            remainder = int(match.group(3))
            result = quotient * divisor + remainder
            return [
                CalculationStep(
                    description=f"逆运算：@=商×除数+余数",
                    operation="逆运算",
                    result=result,
                    formula=f"@={quotient}×{divisor}+{remainder}={result}"
                )
            ]
        # 2. 逆运算：@÷9=2······3
        match = re.match(r'@÷(\d+)=([\d]+)······([\d]+)', expr)
        if match:
            divisor = int(match.group(1))
            quotient = int(match.group(2))
            remainder = int(match.group(3))
            result = quotient * divisor + remainder
            return [
                CalculationStep(
                    description=f"逆运算：@=商×除数+余数",
                    operation="逆运算",
                    result=result,
                    formula=f"@={quotient}×{divisor}+{remainder}={result}"
                )
            ]
        # 3. 逆运算：11÷@=3······2 形式
        match = re.match(r'(\d+)÷@=([\d]+)······([\d]+)', expr)
        if match:
            dividend = int(match.group(1))
            quotient = int(match.group(2))
            remainder = int(match.group(3))
            # @ = (dividend - remainder) // quotient
            if quotient == 0:
                return [CalculationStep(description="商为0，无法计算", operation="错误", result="错误")]
            divisor = (dividend - remainder) // quotient
            return [
                CalculationStep(
                    description=f"逆运算：@=(被除数-余数)÷商",
                    operation="逆运算",
                    result=divisor,
                    formula=f"@=({dividend}-{remainder})÷{quotient}={divisor}"
                )
            ]
        def compare_and_compute(factor: int, operator: str, target: int) -> List[CalculationStep]:
            result = target // factor
            remainder = target % factor
            description=f"最大估值：@=目标数÷因数取整"
            formula_text = f"@={target}÷{factor}={result}...{remainder}"
            print(formula_text)
            if remainder == 0:
                formula_text = f"{target}x{factor}={result}"
            if  remainder >= 0 and operator == '>':
                result = int(result) + 1
                formula_text += f";因为余数{remainder}≥0，满足‘>’条件，结果+1"
            elif remainder == 0 and operator == '<':
                result = int(result) - 1
                formula_text += f";因为余数{remainder}=0，满足‘<’条件，结果-1"
            if operator == '=':
                description=f"直接整除"
            
            return [
                CalculationStep(
                    description=description,
                    operation="乘法转除法",
                    result=result,
                    formula=formula_text
                )
            ]
        # 4. 最大估值：@×8>49 或 7×@>18
        match = re.match(r'@×(\d+)([><=]?)(\d+)', expr)
        if not match:
            match = re.match(r'(\d+)×@([><=]?)(\d+)', expr)
        if match:
            factor = int(match.group(1))
            operator = match.group(2)
            target = int(match.group(3))
            result = target // factor
            return compare_and_compute(factor, expr[expr.index(str(target))-1], target)
        # 5. 默认原有带余数除法
        numbers = formula.get_numbers()
        if len(numbers) < 2:
            return []
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        if divisor == 0:
            return [CalculationStep(description="除数为0，无法计算", operation="错误", result="错误")]
        quotient = dividend // divisor
        remainder = dividend % divisor
        steps = [
            CalculationStep(
                description=f"计算整数商：{dividend} ÷ {divisor}",
                operation="取整商",
                result=quotient,
                formula=f"{dividend} ÷ {divisor} = {quotient}"
            ),
            CalculationStep(
                description=f"计算余数：{dividend} % {divisor}",
                operation="取余数",
                result=remainder,
                formula=f"{dividend} % {divisor} = {remainder}"
            ),
            CalculationStep(
                description="组合最终结果",
                operation="格式化为‘商······余数’",
                result=f"{quotient}······{remainder}",
                formula=f"{dividend} ÷ {divisor} = {quotient}······{remainder}"
            )
        ]
        return steps
