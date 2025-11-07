"""
分数除法算子 - 分数÷分数
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType


class FractionDivideCalculator(FractionCalculator):
    """分数除法算子"""
    
    def __init__(self):
        super().__init__("分数除法", "除以分数等于乘以倒数", priority=5)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配分数除法问题，支持分数÷分数、分数÷整数、整数÷分数"""
        if problem.operation != OperationType.DIVIDE:
            return {"matched": False, "score": 0.0, "reason": "不是除法"}
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        dividend = problem.operands[0]
        divisor = problem.operands[1]
        # 被除数、除数均可为分数或整数
        is_dividend_fraction = (
            getattr(dividend, 'fraction_type', None) in [FractionType.PROPER, FractionType.IMPROPER, FractionType.MIXED]
            or dividend.fraction.denominator != 1
        )
        is_dividend_integer = dividend.fraction.denominator == 1
        is_divisor_fraction = (
            getattr(divisor, 'fraction_type', None) in [FractionType.PROPER, FractionType.IMPROPER, FractionType.MIXED]
            or divisor.fraction.denominator != 1
        )
        is_divisor_integer = divisor.fraction.denominator == 1
        # 只要有一方是分数即可
        if (is_dividend_fraction or is_divisor_fraction):
            return {"matched": True, "score": 1.0, "reason": "支持整数÷分数、分数÷整数、分数÷分数"}
        return {"matched": False, "score": 0.0, "reason": "不支持的除法类型"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行分数除法，支持整数÷分数、分数÷整数、分数÷分数"""
        try:
            dividend_op, divisor_op = problem.operands  # 被除数，除数
            steps = []
            # 步骤1：检查除数不为0
            if divisor_op.fraction.numerator == 0:
                return FractionResult(
                    success=False,
                    error="除数不能为0"
                )
            steps.append(FractionStep(
                description=f"检查除数{divisor_op.fraction}不为0",
                operation="检查除数非零",
                result="除数非零，可以计算"
            ))
            # 步骤2：将带分数转为假分数，整数直接转为分母为1的分数
            def to_fraction(op):
                if getattr(op, 'is_mixed', False):
                    return Fraction(op.whole_part * op.fraction.denominator + op.fraction.numerator, op.fraction.denominator)
                return op.fraction
            dividend = to_fraction(dividend_op)
            divisor = to_fraction(divisor_op)
            if getattr(dividend_op, 'is_mixed', False):
                steps.append(FractionStep(
                    description=f"被除数转假分数：{dividend_op.raw} → {dividend}",
                    operation="转为假分数",
                    result=str(dividend)
                ))
            if getattr(divisor_op, 'is_mixed', False):
                steps.append(FractionStep(
                    description=f"除数转假分数：{divisor_op.raw} → {divisor}",
                    operation="转为假分数",
                    result=str(divisor)
                ))
            # 步骤3：将除法转为乘法（取倒数）
            reciprocal = Fraction(divisor.denominator, divisor.numerator)
            steps.append(FractionStep(
                description=f"除以分数等于乘以倒数：{dividend} ÷ {divisor} = {dividend} × {reciprocal}",
                operation="取倒数并转换为乘法",
                result=f"{dividend} × {reciprocal}",
                formula="a/b ÷ c/d = a/b × d/c"
            ))
            # 步骤4：执行乘法（交叉约分）
            from math import gcd
            num1, den1 = dividend.numerator, dividend.denominator
            num2, den2 = reciprocal.numerator, reciprocal.denominator
            # 交叉约分
            gcd1 = gcd(abs(num1), abs(den2))
            if gcd1 > 1:
                num1 //= gcd1
                den2 //= gcd1
                steps.append(FractionStep(
                    description=f"交叉约分：{dividend.numerator}与{reciprocal.denominator}的公因子{gcd1}",
                    operation="交叉约分",
                    result=f"约分后：{num1}，{den2}"
                ))
            gcd2 = gcd(abs(num2), abs(den1))
            if gcd2 > 1:
                num2 //= gcd2
                den1 //= gcd2
                steps.append(FractionStep(
                    description=f"交叉约分：{reciprocal.numerator}与{dividend.denominator}的公因子{gcd2}",
                    operation="交叉约分",
                    result=f"约分后：{num2}，{den1}"
                ))
            # 相乘得结果
            result_num = num1 * num2
            result_den = den1 * den2
            result_fraction = Fraction(result_num, result_den)
            steps.append(FractionStep(
                description=f"相乘：({num1}×{num2})/({den1}×{den2}) = {result_fraction}",
                operation="分子分母分别相乘",
                result=str(result_fraction)
            ))
            # 步骤5：最终约分和格式化
            final_result = result_fraction
            if result_fraction.denominator != 1:
                final_gcd = gcd(abs(result_fraction.numerator), result_fraction.denominator)
                if final_gcd > 1:
                    final_result = Fraction(result_fraction.numerator // final_gcd,
                                          result_fraction.denominator // final_gcd)
                    steps.append(FractionStep(
                        description=f"最终约分：{result_fraction} → {final_result}",
                        operation="取得最简分数",
                        result=str(final_result)
                    ))
            # 转为带分数（如需要）
            display_result = final_result
            if (problem.display_mixed and 
                abs(final_result.numerator) >= final_result.denominator and 
                final_result.denominator != 1):
                whole = final_result.numerator // final_result.denominator
                remainder = abs(final_result.numerator) % final_result.denominator
                if remainder == 0:
                    display_result = str(whole)
                else:
                    display_result = f"{whole} {remainder}/{final_result.denominator}"
                steps.append(FractionStep(
                    description=f"转为带分数：{final_result} = {display_result}",
                    operation="转为带分数",
                    result=str(display_result)
                ))
            return FractionResult(
                success=True,
                result=display_result,
                steps=steps,
                step_count=len(steps),
                formula=f"分数除法：{dividend} ÷ {divisor} = {display_result}",
                validation=True
            )
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"分数除法计算失败: {str(e)}"
            )
