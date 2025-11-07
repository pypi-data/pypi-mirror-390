"""
分数比较算子 - 比较分数大小
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class FractionCompareCalculator(FractionCalculator):
    """分数比较算子"""
    
    def __init__(self):
        super().__init__("分数比较", "比较分数大小", priority=3)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配分数比较问题"""
        if problem.operation != OperationType.COMPARE:
            return {"matched": False, "score": 0.0, "reason": "不是比较"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        return {"matched": True, "score": 1.0, "reason": "分数比较"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行分数比较"""
        try:
            operand1, operand2 = problem.operands
            frac1, frac2 = operand1.fraction, operand2.fraction
            steps = []
            
            # 步骤1：检查快速路径
            if frac1.denominator == frac2.denominator:
                # 同分母比较
                steps.append(FractionStep(
                    description=f"同分母分数比较：{frac1} 与 {frac2}，分母都是{frac1.denominator}",
                    operation="同分母分数比较",
                    result="直接比较分子大小"
                ))
                
                if frac1.numerator > frac2.numerator:
                    comparison = ">"
                elif frac1.numerator < frac2.numerator:
                    comparison = "<"
                else:
                    comparison = "="
                
                steps.append(FractionStep(
                    description=f"比较分子：{frac1.numerator} {comparison} {frac2.numerator}",
                    operation="比较分子",
                    result=f"{frac1} {comparison} {frac2}"
                ))
                
            elif frac1.numerator == frac2.numerator:
                # 同分子比较
                steps.append(FractionStep(
                    description=f"同分子分数比较：{frac1} 与 {frac2}，分子都是{frac1.numerator}",
                    operation="同分子分数比较",
                    result="分母小者更大"
                ))
                
                if frac1.denominator < frac2.denominator:
                    comparison = ">"
                elif frac1.denominator > frac2.denominator:
                    comparison = "<"
                else:
                    comparison = "="
                
                steps.append(FractionStep(
                    description=f"比较分母：{frac1.denominator} vs {frac2.denominator}，分母小的分数大",
                    operation="比较分母",
                    result=f"{frac1} {comparison} {frac2}"
                ))
                
            else:
                # 交叉相乘比较
                cross1 = frac1.numerator * frac2.denominator
                cross2 = frac2.numerator * frac1.denominator
                
                steps.append(FractionStep(
                    description=f"交叉相乘比较：{frac1.numerator}×{frac2.denominator} 与 {frac2.numerator}×{frac1.denominator}",
                    operation="交叉相乘比较",
                    result=f"{cross1} 与 {cross2}",
                    formula="a/b ? c/d ⟺ a×d ? c×b"
                ))
                
                if cross1 > cross2:
                    comparison = ">"
                elif cross1 < cross2:
                    comparison = "<"
                else:
                    comparison = "="
                
                steps.append(FractionStep(
                    description=f"比较结果：{cross1} {comparison} {cross2}",
                    operation="比较结果",
                    result=f"{frac1} {comparison} {frac2}"
                ))
            
            return FractionResult(
                success=True,
                result=comparison,
                steps=steps,
                step_count=len(steps),
                formula=f"分数比较：{frac1} {comparison} {frac2}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"分数比较失败: {str(e)}"
            )
