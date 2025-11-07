"""
比值转分数算子 - 形如 a:b = #frac{@}{@}#
"""
from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType

class RatioToFractionCalculator(FractionCalculator):
    """比值转分数算子"""
    def __init__(self):
        super().__init__("比值转分数", "比值转为分数形式", priority=2)

    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配比值转分数问题"""
        # 只处理 operation 为 CONVERT 且表达式有两个整数操作数
        if problem.operation != OperationType.CONVERT:
            return {"matched": False, "score": 0.0, "reason": "不是转换"}
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        if problem.target_format not in ("latex_fraction", 'fraction'):
            return {"matched": False, "score": 0.0, "reason": "目标格式不是分数形式"}
        return {"matched": True, "score": 0.0, "reason": "比值转分数"}

    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行比值转分数"""
        try:
            op1, op2 = problem.operands
            a = op1.fraction.numerator
            b = op2.fraction.numerator
            steps = []
            steps.append(FractionStep(
                description=f"将比值 {a}:{b} 转为分数 #frac{{{a}}}{{{b}}}#",
                operation="比值转分数",
                result=f"#frac{{{a}}}{{{b}}}#"
            ))
            # 检查 a, b 是否有大于1的公约数，进行约分
            from math import gcd
            common_divisor = gcd(a, b)
            if common_divisor > 1:
                a_reduced = a // common_divisor
                b_reduced = b // common_divisor
                steps.append(FractionStep(
                    description=f"约分：分子分母同时除以公约数 {common_divisor}",
                    operation="约分",
                    result=f"#frac{{{a_reduced}}}{{{b_reduced}}}#"
                ))
                a, b = a_reduced, b_reduced
            return FractionResult(
                success=True,
                result=f"#frac{{{a}}}{{{b}}}#",
                steps=steps,
                step_count=len(steps),
                formula=f"{a}:{b}=#frac{{{a}}}{{{b}}}#",
                validation=True
            )
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"比值转分数失败: {str(e)}"
            )
