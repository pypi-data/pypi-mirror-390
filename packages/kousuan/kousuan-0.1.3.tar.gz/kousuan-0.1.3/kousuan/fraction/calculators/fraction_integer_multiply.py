"""
分数乘整数算子
"""

from typing import Dict, Any
from fractions import Fraction
from math import gcd
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType


class FractionIntegerMultiplyCalculator(FractionCalculator):
    """分数乘整数算子"""
    
    def __init__(self):
        super().__init__("分数乘整数", "分数与整数相乘，优先约分", priority=5)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配分数乘整数问题"""
        if problem.operation != OperationType.MULTIPLY:
            return {"matched": False, "score": 0.0, "reason": "不是乘法"}
        
        if len(problem.operands) != 2:
            return {"matched": False, "score": 0.0, "reason": "需要两个操作数"}
        
        # 检查是否有一个分数和一个整数
        op1, op2 = problem.operands
        
        # 检查第一个是分数，第二个是整数
        is_frac_int_1 = (op1.fraction_type in [FractionType.PROPER, FractionType.IMPROPER, FractionType.MIXED] and 
                        op2.fraction_type == FractionType.INTEGER)
        
        # 检查第一个是整数，第二个是分数
        is_int_frac_1 = (op1.fraction_type == FractionType.INTEGER and 
                        op2.fraction_type in [FractionType.PROPER, FractionType.IMPROPER, FractionType.MIXED])
        
        # 额外检查：确保整数的分母确实为1
        if is_frac_int_1:
            is_really_integer = op2.fraction.denominator == 1
        elif is_int_frac_1:
            is_really_integer = op1.fraction.denominator == 1
        else:
            is_really_integer = False
        
        if (is_frac_int_1 or is_int_frac_1) and is_really_integer:
            return {"matched": True, "score": 1.0, "reason": "分数乘整数"}
        else:
            return {"matched": False, "score": 0.0, "reason": "不是分数乘整数"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行分数乘整数"""
        try:
            op1, op2 = problem.operands
            steps = []
            
            # 确定哪个是分数，哪个是整数
            if op1.fraction_type == FractionType.INTEGER:
                integer_val = int(op1.fraction)
                fraction_op = op2
                fraction_val = op2.fraction
            else:
                integer_val = int(op2.fraction)
                fraction_op = op1
                fraction_val = op1.fraction
            
            # 步骤1：处理带分数
            if fraction_op.is_mixed:
                improper = Fraction(fraction_op.whole_part * fraction_val.denominator + fraction_val.numerator,
                                  fraction_val.denominator)
                steps.append(FractionStep(
                    description=f"带分数转假分数：{fraction_op.raw} → {improper}",
                    operation="转为假分数",
                    result=str(improper)
                ))
                fraction_val = improper
            
            # 步骤2：尝试约分整数与分母
            original_int = integer_val
            original_denom = fraction_val.denominator
            
            common_factor = gcd(abs(integer_val), fraction_val.denominator)
            if common_factor > 1:
                integer_val //= common_factor
                new_denom = fraction_val.denominator // common_factor
                
                steps.append(FractionStep(
                    description=f"约分整数与分母：整数{original_int}与分母{original_denom}的公因子{common_factor}",
                    operation="约分整数与分母",
                    result=f"约分后：整数={integer_val}，分母={new_denom}"
                ))
            else:
                new_denom = fraction_val.denominator
                steps.append(FractionStep(
                    description=f"整数{integer_val}与分母{fraction_val.denominator}无公因子，直接相乘",
                    operation="判断是否约分",
                    result="无需约分"
                ))
            
            # 步骤3：分子乘以整数
            new_numerator = fraction_val.numerator * integer_val
            result_fraction = Fraction(new_numerator, new_denom)
            
            steps.append(FractionStep(
                description=f"分子乘以整数：{fraction_val.numerator} × {integer_val} = {new_numerator}",
                operation="分子乘以整数",
                result=f"{new_numerator}/{new_denom}",
                formula=f"(a/b)*n = (a*n)/b"
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
                    if final_result.numerator < 0:
                        display_result = f"-{abs(whole)} {remainder}/{final_result.denominator}"
                    else:
                        display_result = f"{whole} {remainder}/{final_result.denominator}"
                
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
                formula=f"分数乘整数：{fraction_op.raw} × {original_int} = {display_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"分数乘整数计算失败: {str(e)}"
            )
