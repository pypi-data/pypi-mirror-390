"""
异分母分数减法算子 - 通分法
"""

from typing import Dict, Any
from fractions import Fraction
from math import gcd
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionUtils


class DifferentDenominatorSubtractCalculator(FractionCalculator):
    """异分母分数减法算子"""
    
    def __init__(self):
        super().__init__("异分母减法", "通分后相减分子", priority=7)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配异分母减法问题"""
        if problem.operation != OperationType.SUBTRACT:
            return {"matched": False, "score": 0.0, "reason": "不是减法"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        # 检查是否为异分母
        frac1, frac2 = problem.operands[0].fraction, problem.operands[1].fraction
        different_denom = frac1.denominator != frac2.denominator
        
        if different_denom:
            return {"matched": True, "score": 1.0, "reason": "异分母减法"}
        else:
            return {"matched": False, "score": 0.0, "reason": "分母相同"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行异分母减法"""
        try:
            operand1, operand2 = problem.operands
            frac1, frac2 = operand1.fraction, operand2.fraction
            steps = []
            
            # 步骤1：计算最小公倍数(LCM)
            lcm_value = FractionUtils.lcm(frac1.denominator, frac2.denominator)
            
            steps.append(FractionStep(
                description=f"计算分母的最小公倍数：lcm({frac1.denominator}, {frac2.denominator}) = {lcm_value}",
                operation="计算分母的最小公倍数",
                result=f"lcm = {lcm_value}",
                formula=f"公分母：{lcm_value}"
            ))
            
            # 步骤2：通分（调整分子）
            multiplier1 = lcm_value // frac1.denominator
            multiplier2 = lcm_value // frac2.denominator
            
            new_num1 = frac1.numerator * multiplier1
            new_num2 = frac2.numerator * multiplier2
            
            adjusted_frac1 = Fraction(new_num1, lcm_value)
            adjusted_frac2 = Fraction(new_num2, lcm_value)
            
            steps.append(FractionStep(
                description=f"通分：{frac1} = {frac1.numerator}×{multiplier1}/{frac1.denominator}×{multiplier1} = {adjusted_frac1}；"
                           f"{frac2} = {frac2.numerator}×{multiplier2}/{frac2.denominator}×{multiplier2} = {adjusted_frac2}",
                operation="通分调整分子",
                result=f"{adjusted_frac1} - {adjusted_frac2}",
                formula="扩分子保持分数值不变"
            ))
            
            # 步骤3：分子相减
            diff_numerator = new_num1 - new_num2
            result_fraction = Fraction(diff_numerator, lcm_value)
            
            steps.append(FractionStep(
                description=f"分子相减：{new_num1} - {new_num2} = {diff_numerator}",
                operation="分子相减，分母不变",
                result=f"{diff_numerator}/{lcm_value}",
                formula=f"结果 = {diff_numerator}/{lcm_value}"
            ))
            
            # 步骤4：约分
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
            
            # 步骤5：根据需要转为带分数
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
                formula=f"异分母减法：{frac1} - {frac2} = {final_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"异分母减法计算失败: {str(e)}"
            )
