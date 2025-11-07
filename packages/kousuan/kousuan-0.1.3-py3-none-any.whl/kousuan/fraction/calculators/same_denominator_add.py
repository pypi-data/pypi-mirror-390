"""
同分母分数加法算子
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class SameDenominatorAddCalculator(FractionCalculator):
    """同分母分数加法算子"""
    
    def __init__(self):
        super().__init__("同分母加法", "分母相同的分数直接相加分子", priority=6)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配同分母加法问题"""
        if problem.operation != OperationType.ADD:
            return {"matched": False, "score": 0.0, "reason": "不是加法"}
        
        if len(problem.operands) < 2:
            return {"matched": False, "score": 0.0, "reason": "操作数不足"}
        
        # 检查所有分数是否同分母
        first_denom = problem.operands[0].fraction.denominator
        same_denom = all(op.fraction.denominator == first_denom for op in problem.operands)
        
        if same_denom:
            return {"matched": True, "score": 1.0, "reason": "同分母加法"}
        else:
            return {"matched": False, "score": 0.0, "reason": "分母不同"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行同分母加法"""
        try:
            operands = problem.operands
            steps = []
            
            # 步骤1：确认同分母
            common_denom = operands[0].fraction.denominator
            fractions = [op.fraction for op in operands]
            
            steps.append(FractionStep(
                description=f"确认分母相同：{' + '.join(str(f) for f in fractions)}，分母都是{common_denom}",
                operation="确认分母相同",
                result=f"公分母：{common_denom}"
            ))
            
            # 步骤2：分子相加
            sum_numerator = sum(f.numerator for f in fractions)
            result_fraction = Fraction(sum_numerator, common_denom)
            
            numerators_str = ' + '.join(str(f.numerator) for f in fractions)
            steps.append(FractionStep(
                description=f"分子相加：{numerators_str} = {sum_numerator}",
                operation="分子相加",
                result=f"{sum_numerator}/{common_denom}",
                formula=f"结果 = {sum_numerator}/{common_denom}"
            ))
            
            # 步骤3：约分并转换格式
            reduced_result = result_fraction
            if result_fraction.denominator != 1:
                # 检查是否可以约分
                from math import gcd
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
                formula=f"同分母加法：{' + '.join(str(f) for f in fractions)} = {final_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"同分母加法计算失败: {str(e)}"
            )
