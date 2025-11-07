"""
小数转分数算子 - 处理小数转换为分数
"""

from typing import Dict, Any
from fractions import Fraction
from math import gcd
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType


class DecimalToFractionCalculator(FractionCalculator):
    """小数转分数算子"""
    
    def __init__(self):
        super().__init__("小数转分数", "将小数转换为最简分数", priority=11)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配小数转分数问题"""
        if problem.operation != OperationType.CONVERT:
            return {"matched": False, "score": 0.0, "reason": "不是转换"}
        
        if len(problem.operands) != 1:
            return {"matched": False, "score": 0.0, "reason": "需要一个操作数"}
        
        operand = problem.operands[0]
        
        # 检查是否为小数转分数（小数 → 分数格式）
        if (operand.fraction_type == FractionType.DECIMAL and 
            problem.target_format == "latex_fraction"):
            return {"matched": True, "score": 1.0, "reason": "小数转分数"}
        
        return {"matched": False, "score": 0.0, "reason": "不是小数转分数"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行小数转分数"""
        try:
            operand = problem.operands[0]
            decimal_str = operand.raw
            steps = []
            
            # 步骤1：分析小数位数
            if '.' not in decimal_str:
                return FractionResult(
                    success=False,
                    error="不是有效的小数"
                )
            
            integer_part, decimal_part = decimal_str.split('.')
            decimal_places = len(decimal_part)
            
            steps.append(FractionStep(
                description=f"分析小数 {decimal_str}：小数点后有 {decimal_places} 位数字",
                operation="分析小数位数",
                result=f"小数位数：{decimal_places}",
                formula="小数位数决定分母的10的幂次"
            ))
            
            # 步骤2：确定分母
            denominator = 10 ** decimal_places
            
            steps.append(FractionStep(
                description=f"确定分母：小数点后 {decimal_places} 位，分母为 10^{decimal_places} = {denominator}",
                operation="确定分母",
                result=f"分母 = {denominator}",
                formula=f"分母 = 10^{decimal_places}"
            ))
            
            # 步骤3：确定分子
            numerator_str = decimal_str.replace('.', '')  # 去掉小数点
            numerator = int(numerator_str)
            
            steps.append(FractionStep(
                description=f"确定分子：去掉小数点 {decimal_str} → {numerator}",
                operation="确定分子",
                result=f"分子 = {numerator}",
                formula="分子 = 去掉小数点后的数字"
            ))
            
            # 步骤4：形成分数
            original_fraction = Fraction(numerator, denominator)
            
            steps.append(FractionStep(
                description=f"形成分数：{numerator}/{denominator}",
                operation="形成初始分数",
                result=f"{numerator}/{denominator}"
            ))
            
            # 步骤5：化简分数
            common_factor = gcd(numerator, denominator)
            
            if common_factor > 1:
                simplified_numerator = numerator // common_factor
                simplified_denominator = denominator // common_factor
                
                steps.append(FractionStep(
                    description=f"化简分数：找到公因数 {common_factor}",
                    operation="找公因数",
                    result=f"公因数 = {common_factor}"
                ))
                
                steps.append(FractionStep(
                    description=f"约分：{numerator}/{denominator} → {simplified_numerator}/{simplified_denominator}",
                    operation="约分化简",
                    result=f"{simplified_numerator}/{simplified_denominator}",
                    formula=f"分子分母同时除以{common_factor}"
                ))
                
                final_fraction = Fraction(simplified_numerator, simplified_denominator)
            else:
                steps.append(FractionStep(
                    description=f"分数 {numerator}/{denominator} 已是最简分数",
                    operation="检查化简",
                    result=f"{numerator}/{denominator}"
                ))
                final_fraction = original_fraction
            
            # 步骤6：检查是否需要转为带分数
            if abs(final_fraction.numerator) >= final_fraction.denominator:
                whole = final_fraction.numerator // final_fraction.denominator
                remainder = abs(final_fraction.numerator) % final_fraction.denominator
                
                if remainder == 0:
                    display_result = str(whole)
                    steps.append(FractionStep(
                        description=f"结果为整数：{final_fraction} = {whole}",
                        operation="转为整数",
                        result=display_result
                    ))
                else:
                    if problem.display_mixed:
                        if final_fraction.numerator < 0:
                            display_result = f"-{abs(whole)} {remainder}/{final_fraction.denominator}"
                        else:
                            display_result = f"{whole} {remainder}/{final_fraction.denominator}"
                        
                        steps.append(FractionStep(
                            description=f"转为带分数：{final_fraction} = {display_result}",
                            operation="转为带分数",
                            result=display_result
                        ))
                    else:
                        display_result = final_fraction
            else:
                display_result = final_fraction
            
            return FractionResult(
                success=True,
                result=display_result,
                steps=steps,
                step_count=len(steps),
                formula=f"小数转分数：{decimal_str} = {display_result}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"小数转分数失败: {str(e)}"
            )
