"""
比值转数值算子 - 形如 a:b=@，求a÷b
"""
from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType

class RatioToValueCalculator(FractionCalculator):
    """比值转数值算子"""
    def __init__(self):
        super().__init__("比值转数值", "比值转为数值", priority=2)

    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配比值转数值问题 a:b=@"""
        if problem.operation != OperationType.CONVERT:
            return {"matched": False, "score": 0.0, "reason": "不是转换"}
        if len(problem.operands) < 2:
            return {"matched": False, "score": 0.0, "reason": "需要2个已知数和1个未知数"}
        if problem.id != "ratio_to_value":
            return {"matched": False, "score": 0.0, "reason": "目标格式不是数值"}
        return {"matched": True, "score": 1.0, "reason": "比值转数值"}

    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行比值转数值 a:b=@，即a÷b"""
        try:
            ops = problem.operands
            idx_unknown = [i for i, op in enumerate(ops) if getattr(op, 'raw', None) == '@'][0]
            knowns = [op.fraction.numerator for i, op in enumerate(ops) if i != idx_unknown]
            steps = []
            a, b = knowns
            value = round(a / b, 6)
            steps.append(FractionStep(
                description=f"{a}:{b}，计算{a}÷{b}={value}",
                operation="比值求值",
                result=str(value)
            ))
            return FractionResult(
                success=True,
                result=str(value),
                steps=steps,
                step_count=len(steps),
                formula=f"{a}:{b}=@，{a}÷{b}={value}",
                validation=True
            )
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"比值转数值失败: {str(e)}"
            )
