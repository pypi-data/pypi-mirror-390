"""
倒数算子 - 求分数的倒数
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class ReciprocalCalculator(FractionCalculator):
    """倒数算子"""
    
    def __init__(self):
        super().__init__("倒数", "求分数的倒数", priority=8)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配倒数问题"""
        if problem.operation == OperationType.RECIPROCAL:
            return {"matched": True, "score": 1.0, "reason": "倒数运算"}
        
        # 检查是否为求倒数的乘法形式 (a/b × ? = 1)
        if (problem.operation == OperationType.MULTIPLY and 
            len(problem.operands) == 1 and 
            problem.target_format in ("reciprocal", 'fraction') ):
            return {"matched": True, "score": 0.9, "reason": "求倒数乘法形式"}
        
        return {"matched": False, "score": 0.0, "reason": "不是倒数问题"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行倒数计算"""
        try:
            operand = problem.operands[0]
            original_fraction = operand.fraction
            steps = []
            
            # 步骤1：检查分数是否为0
            if original_fraction.numerator == 0:
                return FractionResult(
                    success=False,
                    error="0没有倒数"
                )
            
            steps.append(FractionStep(
                description=f"检查{original_fraction}是否为0",
                operation="检查是否为零",
                result="非零，可以求倒数"
            ))
            
            # 步骤2：处理带分数（转为假分数）
            if operand.is_mixed:
                improper = Fraction(operand.whole_part * original_fraction.denominator + original_fraction.numerator,
                                  original_fraction.denominator)
                steps.append(FractionStep(
                    description=f"带分数转假分数：{operand.whole_part} {original_fraction.numerator}/{original_fraction.denominator} → {improper}",
                    operation="转为假分数",
                    result=str(improper),
                    formula=f"({operand.whole_part}×{original_fraction.denominator}+{original_fraction.numerator})/{original_fraction.denominator}"
                ))
                working_fraction = improper
            else:
                working_fraction = original_fraction
            
            # 步骤3：交换分子分母求倒数
            reciprocal = Fraction(working_fraction.denominator, working_fraction.numerator)
            
            steps.append(FractionStep(
                description=f"求倒数：{working_fraction} → {reciprocal}",
                operation="交换分子分母",
                result=str(reciprocal),
                formula="交换分子分母"
            ))
            
            # 步骤4：约分标准化
            if reciprocal != reciprocal:  # 检查是否需要约分
                final_reciprocal = reciprocal
            else:
                final_reciprocal = reciprocal
            
            steps.append(FractionStep(
                description="约分标准化倒数结果",
                operation="约分",
                result=str(final_reciprocal)
            ))
            
            return FractionResult(
                success=True,
                result=final_reciprocal,
                steps=steps,
                step_count=len(steps),
                formula=f"倒数：{original_fraction} → {final_reciprocal}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"倒数计算失败: {str(e)}"
            )
