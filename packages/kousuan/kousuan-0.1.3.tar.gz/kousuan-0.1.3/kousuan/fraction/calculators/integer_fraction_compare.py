"""
整数与分数比较算子 - 比较整数和分数的大小
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, to_latex


class IntegerFractionCompareCalculator(FractionCalculator):
    """整数与分数比较算子"""
    def __init__(self):
        super().__init__("整数与分数比较", "比较整数和分数的大小", priority=5)

    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配整数与分数比较问题"""
        if problem.operation != OperationType.COMPARE:
            return {"matched": False, "score": 0.0, "reason": "不是比较"}
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        op1 = problem.operands[0]
        if isinstance(op1.fraction, Fraction) and not op1.fraction.is_integer:
            return {"matched": False, "score": 0.0, "reason": "不是整数与分数比较"}
        return {"matched": True, "score": 5.0, "reason": "整数与分数比较"}

    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行整数与分数比较，保证比较方向与表达式顺序一致"""
        try:
            op1, op2 = problem.operands
            # 判断左右两侧哪个是整数，哪个是分数
            left, right = op1, op2
            left_str = str(left.fraction)
            right_str = to_latex(right.fraction)
            # 标记左右类型
            left_is_int = True if op2.original_format == 'latex' else False
            # 统一将整数和分数都转为 Fraction
            left_frac = left.fraction
            right_frac = right.fraction
            steps = []
            # 整数转分数步骤
            if left_is_int:
                steps.append(FractionStep(
                    description=f"将整数 {left_str} 转为分数 {to_latex(left_frac)}",
                    operation="整数转分数",
                    result=str(left_frac)
                ))
            else:
                steps.append(FractionStep(
                    description=f"将整数 {right_str} 转为分数 {to_latex(right_frac)}",
                    operation="整数转分数",
                    result=str(right_frac)
                ))
            # 交叉相乘
            cross_left = left_frac.numerator * right_frac.denominator
            cross_right = right_frac.numerator * left_frac.denominator
            steps.append(FractionStep(
                description=f"交叉相乘比较：{left_frac.numerator}×{right_frac.denominator} 与 {right_frac.numerator}×{left_frac.denominator}",
                operation="cross_multiply_compare",
                result=f"{cross_left} 与 {cross_right}",
                formula="a/b ? c/d ⟺ a×d ? c×b"
            ))
            if cross_left > cross_right:
                comparison = ">"
            elif cross_left < cross_right:
                comparison = "<"
            else:
                comparison = "="
            steps.append(FractionStep(
                description=f"比较结果：{cross_left} {comparison} {cross_right}",
                operation="比较结果",
                result=f"{left_str} {comparison} {right_str}"
            ))
            return FractionResult(
                success=True,
                result=comparison,
                steps=steps,
                name="整数与分数比较",
                step_count=len(steps),
                formula=f"整数与分数比较：{left_str} {comparison} {right_str}",
                validation=True
            )
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"整数与分数比较失败: {str(e)}"
            )
