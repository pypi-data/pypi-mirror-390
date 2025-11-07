"""
同分子分数比较算子 - 分子相同时比较分母
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class SameNumeratorCompareCalculator(FractionCalculator):
    """同分子分数比较算子"""
    
    def __init__(self):
        super().__init__("同分子比较", "分子相同时，分母小的分数大", priority=2)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配同分子比较问题"""
        if problem.operation != OperationType.COMPARE:
            return {"matched": False, "score": 0.0, "reason": "不是比较"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        frac1, frac2 = problem.operands[0].fraction, problem.operands[1].fraction
        
        # 检查分子是否相同
        if frac1.numerator == frac2.numerator and frac1.denominator != frac2.denominator:
            return {"matched": True, "score": 1.0, "reason": "同分子比较"}
        
        return {"matched": False, "score": 0.0, "reason": "分子不同"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行同分子比较"""
        try:
            operand1, operand2 = problem.operands
            frac1, frac2 = operand1.fraction, operand2.fraction
            steps = []
            
            # 步骤1：确认同分子
            common_numerator = frac1.numerator
            
            steps.append(FractionStep(
                description=f"确认分子相同：{frac1} 和 {frac2}，分子都是 {common_numerator}",
                operation="确认同分子",
                result=f"公分子：{common_numerator}"
            ))
            
            # 步骤2：解释同分子比较原理
            steps.append(FractionStep(
                description="同分子分数比较原理：分子相同时取的份数一样，分母越小每份越大",
                operation="比较原理说明",
                result="分母小的分数大",
                formula="分子相同时：分母小 → 分数大"
            ))
            
            # 步骤3：比较分母
            denom1, denom2 = frac1.denominator, frac2.denominator
            
            steps.append(FractionStep(
                description=f"比较分母：{denom1} 与 {denom2}",
                operation="比较分母",
                result=f"{denom1} {'<' if denom1 < denom2 else '>' if denom1 > denom2 else '='} {denom2}"
            ))
            
            # 步骤4：得出结论
            if denom1 < denom2:
                comparison = ">"
                explanation = f"因为 {denom1} < {denom2}，所以 {frac1} > {frac2}"
            elif denom1 > denom2:
                comparison = "<"
                explanation = f"因为 {denom1} > {denom2}，所以 {frac1} < {frac2}"
            else:
                comparison = "="
                explanation = f"因为 {denom1} = {denom2}，所以 {frac1} = {frac2}"
            
            steps.append(FractionStep(
                description=explanation,
                operation="得出结论",
                result=f"{frac1} {comparison} {frac2}",
                formula="同分子：分母小的分数大"
            ))
            
            return FractionResult(
                success=True,
                result=comparison,
                steps=steps,
                step_count=len(steps),
                formula=f"同分子比较：{frac1} {comparison} {frac2}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"同分子比较失败: {str(e)}"
            )
