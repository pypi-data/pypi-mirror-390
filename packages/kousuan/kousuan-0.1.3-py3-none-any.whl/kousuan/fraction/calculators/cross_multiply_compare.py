"""
交叉相乘比较算子 - 用交叉相乘法比较分数大小
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class CrossMultiplyCompareCalculator(FractionCalculator):
    """交叉相乘比较算子"""
    
    def __init__(self):
        super().__init__("交叉相乘比较", "用交叉相乘法快速比较分数大小", priority=4)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配交叉相乘比较问题"""
        if problem.operation != OperationType.COMPARE:
            return {"matched": False, "score": 0.0, "reason": "不是比较"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        frac1, frac2 = problem.operands[0].fraction, problem.operands[1].fraction
        
        # 适用于分子分母都不相同的情况
        if (frac1.numerator != frac2.numerator and 
            frac1.denominator != frac2.denominator):
            return {"matched": True, "score": 0.8, "reason": "异分子异分母比较"}
        
        return {"matched": False, "score": 0.0, "reason": "有相同分子或分母，不适用交叉相乘"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行交叉相乘比较"""
        try:
            operand1, operand2 = problem.operands
            frac1, frac2 = operand1.fraction, operand2.fraction
            steps = []
            
            # 步骤1：说明交叉相乘方法
            steps.append(FractionStep(
                description=f"比较 {frac1} 和 {frac2}，分子分母都不相同，使用交叉相乘法",
                operation="选择方法",
                result="采用交叉相乘法快速比较"
            ))
            
            # 步骤2：解释交叉相乘原理
            steps.append(FractionStep(
                description="交叉相乘原理：a/b 与 c/d 比较 ⟺ a×d 与 c×b 比较",
                operation="方法原理",
                result="交叉相乘后比较积的大小",
                formula="a/b ? c/d ⟺ a×d ? c×b"
            ))
            
            # 步骤3：计算交叉乘积
            cross1 = frac1.numerator * frac2.denominator  # a×d
            cross2 = frac2.numerator * frac1.denominator  # c×b
            
            steps.append(FractionStep(
                description=f"计算交叉乘积：{frac1.numerator}×{frac2.denominator} = {cross1}",
                operation="计算积1",
                result=f"积1 = {cross1}"
            ))
            
            steps.append(FractionStep(
                description=f"计算交叉乘积：{frac2.numerator}×{frac1.denominator} = {cross2}",
                operation="计算积2",
                result=f"积2 = {cross2}"
            ))
            
            # 步骤4：比较乘积
            steps.append(FractionStep(
                description=f"比较乘积：{cross1} 与 {cross2}",
                operation="比较乘积",
                result=f"{cross1} {'>' if cross1 > cross2 else '<' if cross1 < cross2 else '='} {cross2}"
            ))
            
            # 步骤5：得出结论
            if cross1 > cross2:
                comparison = ">"
                explanation = f"因为 {cross1} > {cross2}，所以 {frac1} > {frac2}"
            elif cross1 < cross2:
                comparison = "<"
                explanation = f"因为 {cross1} < {cross2}，所以 {frac1} < {frac2}"
            else:
                comparison = "="
                explanation = f"因为 {cross1} = {cross2}，所以 {frac1} = {frac2}"
            
            steps.append(FractionStep(
                description=explanation,
                operation="得出结论",
                result=f"{frac1} {comparison} {frac2}",
                formula="积大的对应分数大"
            ))
            
            return FractionResult(
                success=True,
                result=comparison,
                steps=steps,
                step_count=len(steps),
                formula=f"交叉相乘比较：{frac1} {comparison} {frac2}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"交叉相乘比较失败: {str(e)}"
            )
