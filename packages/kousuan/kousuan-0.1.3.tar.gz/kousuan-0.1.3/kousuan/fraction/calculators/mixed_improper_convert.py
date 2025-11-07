"""
带分数与假分数互转算子
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType


class MixedImproperConvertCalculator(FractionCalculator):
    """带分数与假分数互转算子"""
    
    def __init__(self):
        super().__init__("带分数假分数互转", "带分数与假分数相互转换", priority=4)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配互转问题"""
        if problem.operation != OperationType.CONVERT:
            return {"matched": False, "score": 0.0, "reason": "不是转换"}
        
        if len(problem.operands) != 1:
            return {"matched": False, "score": 0.0, "reason": "需要一个操作数"}
        
        operand = problem.operands[0]
        
        # 检查是否为带分数转假分数
        if operand.is_mixed and problem.target_format == "improper":
            return {"matched": True, "score": 1.0, "reason": "带分数转假分数"}
        
        # 检查是否为假分数转带分数
        if (operand.fraction_type == FractionType.IMPROPER and 
            problem.target_format == "mixed"):
            return {"matched": True, "score": 1.0, "reason": "假分数转带分数"}
        
        return {"matched": False, "score": 0.0, "reason": "不匹配的转换类型"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行互转"""
        try:
            operand = problem.operands[0]
            steps = []
            
            if operand.is_mixed:
                return self._mixed_to_improper(operand, steps)
            else:
                return self._improper_to_mixed(operand, steps, problem)
                
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"带分数假分数互转失败: {str(e)}"
            )
    
    def _mixed_to_improper(self, operand, steps: list) -> FractionResult:
        """带分数转假分数"""
        whole = operand.whole_part
        fraction = operand.fraction
        
        # 计算假分数
        improper_numerator = whole * fraction.denominator + fraction.numerator
        improper_fraction = Fraction(improper_numerator, fraction.denominator)
        
        steps.append(FractionStep(
            description=f"带分数转假分数：{whole} {fraction} → ({whole}×{fraction.denominator}+{fraction.numerator})/{fraction.denominator}",
            operation="to_improper_or_to_mixed",
            result=str(improper_fraction),
            formula=f"improper = whole*denom + numer = {whole}×{fraction.denominator}+{fraction.numerator} = {improper_numerator}"
        ))
        
        return FractionResult(
            success=True,
            result=improper_fraction,
            steps=steps,
            step_count=len(steps),
            formula=f"带分数转假分数：{operand.raw} → {improper_fraction}",
            validation=True
        )
    
    def _improper_to_mixed(self, operand, steps: list, problem: FractionProblem) -> FractionResult:
        """假分数转带分数"""
        fraction = operand.fraction
        
        # 计算带分数
        whole = fraction.numerator // fraction.denominator
        remainder = abs(fraction.numerator) % fraction.denominator
        
        if remainder == 0:
            # 结果是整数
            result = str(whole)
            steps.append(FractionStep(
                description=f"假分数转整数：{fraction} = {whole}",
                operation="to_integer",
                result=result
            ))
        else:
            # 结果是带分数
            if fraction.numerator < 0:
                result = f"-{abs(whole)} {remainder}/{fraction.denominator}"
            else:
                result = f"{whole} {remainder}/{fraction.denominator}"
            
            steps.append(FractionStep(
                description=f"假分数转带分数：{fraction} = {result}",
                operation="to_mixed",
                result=result,
                formula=f"整数部分={whole}, 余数={remainder}"
            ))
        
        return FractionResult(
            success=True,
            result=result,
            steps=steps,
            step_count=len(steps),
            formula=f"假分数转带分数：{fraction} → {result}",
            validation=True
        )
