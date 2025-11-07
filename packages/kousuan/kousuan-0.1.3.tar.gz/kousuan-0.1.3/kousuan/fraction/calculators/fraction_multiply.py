"""
分数乘法算子 - 分数×分数
"""

from typing import Dict, Any
from fractions import Fraction
from math import gcd
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType


class FractionMultiplyCalculator(FractionCalculator):
    """分数乘法算子"""
    
    def __init__(self):
        super().__init__("分数乘法", "分数相乘，优先交叉约分", priority=5)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配分数乘法问题"""
        if problem.operation != OperationType.MULTIPLY:
            return {"matched": False, "score": 0.0, "reason": "不是乘法"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        # 检查是否都是分数
        has_fraction = any(op.fraction_type in [FractionType.PROPER, FractionType.IMPROPER, FractionType.MIXED] 
                          for op in problem.operands)
        
        if has_fraction:
            return {"matched": True, "score": 0.9, "reason": "分数乘法"}
        else:
            return {"matched": False, "score": 0.0, "reason": "不包含分数"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行分数乘法"""
        try:
            operand1, operand2 = problem.operands
            steps = []
            
            # 步骤1：将带分数转为假分数
            frac1 = operand1.fraction
            frac2 = operand2.fraction
            
            if operand1.is_mixed:
                improper1 = Fraction(operand1.whole_part * frac1.denominator + frac1.numerator, frac1.denominator)
                steps.append(FractionStep(
                    description=f"带分数转假分数：{operand1.raw} → {improper1}",
                    operation="转为假分数",
                    result=str(improper1)
                ))
                frac1 = improper1
            
            if operand2.is_mixed:
                improper2 = Fraction(operand2.whole_part * frac2.denominator + frac2.numerator, frac2.denominator)
                steps.append(FractionStep(
                    description=f"带分数转假分数：{operand2.raw} → {improper2}",
                    operation="转为假分数", 
                    result=str(improper2)
                ))
                frac2 = improper2
            
            # 步骤2：交叉约分
            num1, den1 = frac1.numerator, frac1.denominator
            num2, den2 = frac2.numerator, frac2.denominator
            
            # 约分 num1 与 den2
            gcd1 = gcd(abs(num1), abs(den2))
            if gcd1 > 1:
                num1 //= gcd1
                den2 //= gcd1
                steps.append(FractionStep(
                    description=f"交叉约分：分子{frac1.numerator}与分母{frac2.denominator}的公因子{gcd1}",
                    operation="交叉约分",
                    result=f"约分后：{num1}，{den2}"
                ))
            
            # 约分 num2 与 den1
            gcd2 = gcd(abs(num2), abs(den1))
            if gcd2 > 1:
                num2 //= gcd2
                den1 //= gcd2
                steps.append(FractionStep(
                    description=f"交叉约分：分子{frac2.numerator}与分母{frac1.denominator}的公因子{gcd2}",
                    operation="交叉约分",
                    result=f"约分后：{num2}，{den1}"
                ))
            
            # 步骤3：分子相乘，分母相乘
            result_num = num1 * num2
            result_den = den1 * den2
            result_fraction = Fraction(result_num, result_den)
            
            steps.append(FractionStep(
                description=f"分子相乘，分母相乘：#frac{{({num1}×{num2})}}{{({den1}×{den2})}}# = #frac{{{result_num}}}{{{result_den}}}#",
                operation="分子分母分别相乘",
                result=str(result_fraction),
                formula="#frac{a}{b}#×#frac{c}{d}# = #frac{a×c}{b×d}#"
            ))
            
            # 步骤4：最终约分
            final_result = result_fraction
            if result_fraction.denominator != 1:
                final_gcd = gcd(abs(result_fraction.numerator), result_fraction.denominator)
                if final_gcd > 1:
                    final_result = Fraction(result_fraction.numerator // final_gcd,
                                          result_fraction.denominator // final_gcd)
                    steps.append(FractionStep(
                        description=f"最终约分：{result_fraction} → {final_result}",
                        operation="取得最简分数",
                        result=str(final_result)
                    ))
            
            # 步骤5：根据需要转为带分数
            display_result = final_result
            if (problem.display_mixed and 
                abs(final_result.numerator) >= final_result.denominator and 
                final_result.denominator != 1):
                
                whole = final_result.numerator // final_result.denominator
                remainder = abs(final_result.numerator) % final_result.denominator
                
                if remainder == 0:
                    display_result = str(whole)
                else:
                    display_result = f"{whole}#frac{{{remainder}}}{{{final_result.denominator}}}#"
                
                steps.append(FractionStep(
                    description=f"转为带分数：{final_result} = {display_result}",
                    operation="转为带分数",
                    result=str(display_result)
                ))
            
            return FractionResult(
                success=True,
                result=display_result,
                steps=steps,
                step_count=len(steps),
                formula=f"分数乘法：{frac1}×{frac2} = {display_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"分数乘法计算失败: {str(e)}"
            )
