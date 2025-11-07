"""
异分母分数加法算子 - 通分法
"""

from typing import Dict, Any
from fractions import Fraction
from math import gcd
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionUtils


class DifferentDenominatorAddCalculator(FractionCalculator):
    """异分母分数加法算子"""
    
    def __init__(self):
        super().__init__("异分母加法", "通分后相加分子", priority=7)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配异分母加法问题"""
        if problem.operation != OperationType.ADD:
            return {"matched": False, "score": 0.0, "reason": "不是加法"}
        
        if len(problem.operands) < 2:
            return {"matched": False, "score": 0.0, "reason": "操作数不足"}
        
        # 检查是否为异分母
        denominators = [op.fraction.denominator for op in problem.operands]
        different_denom = len(set(denominators)) > 1
        
        if different_denom:
            return {"matched": True, "score": 1.0, "reason": "异分母加法"}
        else:
            return {"matched": False, "score": 0.0, "reason": "分母相同"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行异分母加法"""
        try:
            operands = problem.operands
            fractions = [op.fraction for op in operands]
            steps = []
            
            # 步骤1：计算最小公倍数(LCM)
            denominators = [f.denominator for f in fractions]
            lcm_value = denominators[0]
            for denom in denominators[1:]:
                lcm_value = FractionUtils.lcm(lcm_value, denom)
            
            steps.append(FractionStep(
                description=f"计算分母的最小公倍数：lcm({', '.join(map(str, denominators))}) = {lcm_value}",
                operation="计算分母的最小公倍数",
                result=f"lcm = {lcm_value}",
                formula=f"公分母：{lcm_value}"
            ))
            
            # 步骤2：通分（调整分子）- 修正这里的计算
            adjusted_fractions = []
            adjustment_details = []
            adjusted_numerators = []  # 单独记录调整后的分子
            
            for i, fraction in enumerate(fractions):
                multiplier = lcm_value // fraction.denominator
                new_numerator = fraction.numerator * multiplier
                adjusted_fraction = Fraction(new_numerator, lcm_value)
                adjusted_fractions.append(adjusted_fraction)
                adjusted_numerators.append(new_numerator)  # 记录实际的分子
                
                adjustment_details.append(
                    f"{fraction} = {fraction.numerator}×{multiplier}/{fraction.denominator}×{multiplier} = {new_numerator}/{lcm_value}"
                )
            
            steps.append(FractionStep(
                description="通分各分数：" + "；".join(adjustment_details),
                operation="通分各分数",
                result=" + ".join(str(f) for f in adjusted_fractions),
                formula="扩分子保持分数值不变"
            ))
            
            # 步骤3：相加调整后的分子 - 使用正确的分子
            sum_numerator = sum(adjusted_numerators)  # 使用调整后的分子
            result_fraction = Fraction(sum_numerator, lcm_value)
            
            numerators_str = " + ".join(str(num) for num in adjusted_numerators)
            steps.append(FractionStep(
                description=f"分子相加：{numerators_str} = {sum_numerator}",
                operation="分子相加",
                result=f"{sum_numerator}/{lcm_value}",
                formula=f"结果 = {sum_numerator}/{lcm_value}"
            ))
            
            # 步骤4：约分 - Python的Fraction会自动约分
            reduced_result = result_fraction  # Fraction构造时会自动约分
            
            # 如果约分了，添加约分步骤说明
            if result_fraction.numerator != sum_numerator or result_fraction.denominator != lcm_value:
                from math import gcd
                common_factor = gcd(sum_numerator, lcm_value)
                steps.append(FractionStep(
                    description=f"约分：{sum_numerator}/{lcm_value} → {reduced_result}",
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
                name="异分母加法",
                step_count=len(steps),
                formula=f"异分母加法：{' + '.join(str(f) for f in fractions)} = {final_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"异分母加法计算失败: {str(e)}"
            )
