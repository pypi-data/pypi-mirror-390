"""
约分算子 - 将分数化为最简形式
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionUtils


class ReduceFractionCalculator(FractionCalculator):
    """约分算子"""
    
    def __init__(self):
        super().__init__("约分", "将分数化为最简形式，可转为带分数", priority=10)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配约分问题"""
        if problem.operation == OperationType.REDUCE and len(problem.operands) == 1:
            operand = problem.operands[0]
            # 检查是否需要约分
            gcd = FractionUtils.gcd(operand.fraction.numerator, operand.fraction.denominator)
            needs_reduce = gcd > 1
            return {
                "matched": True,
                "score": 0.9 if needs_reduce else 0.5,
                "reason": "单分数约分" if needs_reduce else "已是最简分数"
            }
        return {"matched": False, "score": 0.0, "reason": "不是约分问题"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行约分"""
        try:
            operand = problem.operands[0]
            original_fraction = operand.fraction
            steps = []
            
            # 步骤1：标准化分子分母，确保分母为正
            normalized = Fraction(original_fraction.numerator, original_fraction.denominator)
            if normalized.denominator < 0:
                normalized = Fraction(-normalized.numerator, -normalized.denominator)
            
            steps.append(FractionStep(
                description=f"标准化分数：{original_fraction} → {normalized}",
                operation="标准化分数",
                result=str(normalized),
                formula="确保分母为正"
            ))
            
            # 步骤2：计算最大公约数并约分
            gcd = FractionUtils.gcd(abs(normalized.numerator), normalized.denominator)
            if gcd > 1:
                reduced = Fraction(normalized.numerator // gcd, normalized.denominator // gcd)
                steps.append(FractionStep(
                    description=f"计算gcd({abs(normalized.numerator)}, {normalized.denominator}) = {gcd}",
                    operation="计算最大公约数",
                    result=f"gcd = {gcd}"
                ))
                
                steps.append(FractionStep(
                    description=f"约分：{normalized.numerator}/{normalized.denominator} → {reduced.numerator}/{reduced.denominator}",
                    operation="约分",
                    result=str(reduced),
                    formula=f"分子分母同时除以{gcd}"
                ))
            else:
                reduced = normalized
                steps.append(FractionStep(
                    description="分数已是最简形式",
                    operation="最简分数检查",
                    result=str(reduced)
                ))
            
            # 步骤3：根据需要转为带分数
            if problem.display_mixed and abs(reduced.numerator) >= reduced.denominator:
                whole = reduced.numerator // reduced.denominator
                remainder = abs(reduced.numerator) % reduced.denominator
                
                if remainder == 0:
                    final_result = str(whole)
                    steps.append(FractionStep(
                        description=f"转为整数：{reduced} = {whole}",
                        operation="转为整数",
                        result=final_result
                    ))
                else:
                    mixed_str = f"{whole} {remainder}/{reduced.denominator}"
                    steps.append(FractionStep(
                        description=f"转为带分数：{reduced} = {mixed_str}",
                        operation="转为带分数",
                        result=mixed_str,
                        formula=f"整数部分={whole}, 余数={remainder}"
                    ))
                    final_result = mixed_str
            else:
                final_result = reduced
            
            return FractionResult(
                success=True,
                result=final_result,
                steps=steps,
                step_count=len(steps),
                formula=f"约分：{original_fraction} → {final_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"约分计算失败: {str(e)}"
            )
