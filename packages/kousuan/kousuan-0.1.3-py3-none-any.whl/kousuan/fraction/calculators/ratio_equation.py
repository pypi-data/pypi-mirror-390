"""
比值等值算子 - 形如 a:b = c:d，求未知数
"""
from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType

class RatioEquationCalculator(FractionCalculator):
    """比值等值算子"""
    def __init__(self):
        super().__init__("比值等值", "比值等式求未知数", priority=2)

    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配比值等值问题 a:b = c:d，且有一个未知数。无EQUATION类型时采用CONVERT。"""
        if problem.operation not in [OperationType.CONVERT]:
            return {"matched": False, "score": 0.0, "reason": "不是等式"}
        if problem.id != "ratio_equation":
            return {"matched": False, "score": 0.0, "reason": "不是比值等式"}
        if len(problem.operands) != 4:
            return {"matched": False, "score": 0.0, "reason": "需要4个操作数"}
        # 检查有且仅有一个未知数
        unknown_count = sum(1 for op in problem.operands if getattr(op, 'is_unknown', False))
        if unknown_count != 1:
            return {"matched": False, "score": 0.0, "reason": "未知数数量不为1"}
        return {"matched": True, "score": 1.0, "reason": "比值等值方程"}

    def solve(self, problem: FractionProblem) -> FractionResult:
        """解比值等值方程 a:b = c:d，求未知数"""
        try:
            ops = problem.operands
            # 标记未知数位置
            idx_unknown = [i for i, op in enumerate(ops) if getattr(op, 'is_unknown', False)][0]
            knowns = [op.fraction.numerator for i, op in enumerate(ops) if i != idx_unknown]
            steps = []
            # a:b = c:d => a*d = b*c
            # 求未知数
            if idx_unknown == 0:
                # x:b = c:d => x = b*c/d
                b, c, d = knowns
                x = b * c // d
                steps.append(FractionStep(
                    description=f"x:b = c:d，x = b×c/d = {b}×{c}/{d} = {x}",
                    operation="未知数求解",
                    result=str(x)
                ))
            elif idx_unknown == 1:
                # a:x = c:d => x = a*d/c
                a, c, d = knowns
                x = a * d // c
                steps.append(FractionStep(
                    description=f"a:x = c:d，x = a×d/c = {a}×{d}/{c} = {x}",
                    operation="未知数求解",
                    result=str(x)
                ))
            elif idx_unknown == 2:
                # a:b = x:d => x = a*d/b
                a, b, d = knowns
                x = a * d // b
                steps.append(FractionStep(
                    description=f"a:b = x:d，x = a×d/b = {a}×{d}/{b} = {x}",
                    operation="未知数求解",
                    result=str(x)
                ))
            elif idx_unknown == 3:
                # a:b = c:x => x = b*c/a
                a, b, c = knowns
                x = b * c // a
                steps.append(FractionStep(
                    description=f"a:b = c:x，x = b×c/a = {b}×{c}/{a} = {x}",
                    operation="未知数求解",
                    result=str(x)
                ))
            else:
                return FractionResult(success=False, error="未知数位置错误")
            return FractionResult(
                success=True,
                result=str(x),
                steps=steps,
                step_count=len(steps),
                formula="比值等式求解",
                validation=True
            )
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"比值等值方程求解失败: {str(e)}"
            )
