"""
分数转小数算子 - 处理分数转换为小数
"""
from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType

class FractionToDecimalCalculator(FractionCalculator):
    """分数转小数算子"""
    def __init__(self):
        super().__init__("分数转小数", "将分数转换为小数", priority=11)

    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配分数转小数问题"""
        if problem.operation != OperationType.CONVERT:
            return {"matched": False, "score": 0.0, "reason": "不是转换"}
        if len(problem.operands) != 1:
            return {"matched": False, "score": 0.0, "reason": "需要一个操作数"}
        operand = problem.operands[0]
        # 检查是否为分数转小数（分数 → decimal 格式）
        if operand.fraction_type in [FractionType.PROPER, FractionType.IMPROPER]:
            return {"matched": True, "score": 1.0, "reason": "分数转小数"}
        return {"matched": False, "score": 0.0, "reason": "不是分数转小数"}

    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行分数转小数"""
        try:
            operand = problem.operands[0]
            frac = operand.fraction
            steps = []
            # 步骤1：分子分母直接相除
            steps.append(FractionStep(
                description=f"分子除以分母：{frac.numerator} ÷ {frac.denominator}",
                operation="分子除以分母",
                result=f"{frac.numerator} ÷ {frac.denominator}"
            ))
            # 步骤2：计算小数值
            decimal_value = frac.numerator / frac.denominator
            steps.append(FractionStep(
                description=f"计算小数值：{frac.numerator} ÷ {frac.denominator} = {decimal_value}",
                operation="计算小数",
                result=str(decimal_value)
            ))
            return FractionResult(
                success=True,
                result=str(decimal_value),
                steps=steps,
                step_count=len(steps),
                formula=f"分数转小数：{frac.numerator}/{frac.denominator} = {decimal_value}",
                validation=True
            )
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"分数转小数失败: {str(e)}"
            )
