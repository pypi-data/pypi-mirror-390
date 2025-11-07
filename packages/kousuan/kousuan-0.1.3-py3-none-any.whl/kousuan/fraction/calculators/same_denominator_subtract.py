"""
同分母分数减法算子
"""

from typing import Dict, Any
from fractions import Fraction
from math import gcd
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class SameDenominatorSubtractCalculator(FractionCalculator):
    """同分母分数减法算子"""
    
    def __init__(self):
        super().__init__("同分母减法", "分母相同的分数直接相减分子", priority=6)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配同分母减法问题"""
        if problem.operation != OperationType.SUBTRACT:
            return {"matched": False, "score": 0.0, "reason": "不是减法"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        # 检查是否同分母
        frac1, frac2 = problem.operands[0].fraction, problem.operands[1].fraction
        same_denom = frac1.denominator == frac2.denominator
        
        if same_denom:
            return {"matched": True, "score": 1.0, "reason": "同分母减法"}
        else:
            return {"matched": False, "score": 0.0, "reason": "分母不同"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行同分母减法"""
        try:
            operand1, operand2 = problem.operands
            frac1, frac2 = operand1.fraction, operand2.fraction
            steps = []
            
            # 步骤1：确认同分母
            common_denom = frac1.denominator
            
            steps.append(FractionStep(
                description=f"确认分母相同：{frac1} - {frac2}，分母都是{common_denom}",
                operation="确认分母相同",
                result=f"公分母：{common_denom}"
            ))
            
            # 步骤2：分子相减
            diff_numerator = frac1.numerator - frac2.numerator
            result_fraction = Fraction(diff_numerator, common_denom)
            
            steps.append(FractionStep(
                description=f"分子相减：{frac1.numerator} - {frac2.numerator} = {diff_numerator}",
                operation="分子相减，分母不变",
                result=f"{diff_numerator}/{common_denom}",
                formula=f"结果 = {diff_numerator}/{common_denom}"
            ))
            
            # 步骤3：约分
            reduced_result = result_fraction
            if result_fraction.denominator != 1:
                common_factor = gcd(abs(result_fraction.numerator), result_fraction.denominator)
                if common_factor > 1:
                    reduced_result = Fraction(result_fraction.numerator // common_factor,
                                            result_fraction.denominator // common_factor)
                    steps.append(FractionStep(
                        description=f"约分：{result_fraction} → {reduced_result}",
                        operation="约分",
                        result=str(reduced_result),
                        formula=f"约去公因子{common_factor}"
                    ))
            
            # 步骤4：根据需要转为带分数
            final_result = reduced_result
            if (problem.display_mixed and 
                abs(reduced_result.numerator) >= reduced_result.denominator and 
                reduced_result.denominator != 1):
                
                whole = reduced_result.numerator // reduced_result.denominator
                remainder = abs(reduced_result.numerator) % reduced_result.denominator
                
                if remainder == 0:
                    final_result = str(whole)
                else:
                    if reduced_result.numerator < 0:
                        final_result = f"-{abs(whole)} {remainder}/{reduced_result.denominator}"
                    else:
                        final_result = f"{whole} {remainder}/{reduced_result.denominator}"
                
                steps.append(FractionStep(
                    description=f"转为带分数：{reduced_result} = {final_result}",
                    operation="转为带分数",
                    result=str(final_result)
                ))
            
            return FractionResult(
                success=True,
                result=final_result,
                steps=steps,
                step_count=len(steps),
                formula=f"同分母减法：{frac1} - {frac2} = {final_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"同分母减法计算失败: {str(e)}"
            )
