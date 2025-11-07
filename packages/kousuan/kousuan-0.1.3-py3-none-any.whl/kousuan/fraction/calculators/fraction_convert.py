"""
分数转换算子 - 分数与小数、百分数互转
"""

from typing import Dict, Any
from fractions import Fraction
from decimal import Decimal, getcontext
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType, FractionType

# 设置高精度
getcontext().prec = 28


class FractionConvertCalculator(FractionCalculator):
    """分数转换算子"""
    
    def __init__(self):
        super().__init__("分数转换", "分数与小数、百分数互转", priority=12)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配转换问题"""
        if problem.operation != OperationType.CONVERT:
            return {"matched": False, "score": 0.0, "reason": "不是转换"}
        
        # 检查目标格式
        if problem.target_format in ["decimal", "percent", "latex_fraction"]:
            return {"matched": True, "score": 1.0, "reason": "分数转换"}
        
        return {"matched": False, "score": 0.0, "reason": "不支持的转换格式"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行分数转换"""
        try:
            operand = problem.operands[0]
            fraction = operand.fraction
            target_format = problem.target_format
            steps = []
            
            if target_format == "decimal":
                return self._convert_to_decimal(fraction, steps, problem)
            elif target_format == "percent":
                return self._convert_to_percent(fraction, steps, problem)
            elif target_format == "latex_fraction":
                return self._convert_to_latex(fraction, steps, problem)
            else:
                return FractionResult(
                    success=False,
                    error=f"不支持的转换格式: {target_format}"
                )
                
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"分数转换失败: {str(e)}"
            )
    
    def _convert_to_decimal(self, fraction: Fraction, steps: list, problem: FractionProblem) -> FractionResult:
        """转换为小数"""
        # 步骤1：约分分数
        reduced = fraction
        steps.append(FractionStep(
            description=f"约分分数：{fraction} → {reduced}",
            operation="约分分数",
            result=str(reduced)
        ))
        
        # 步骤2：检查分母的质因数
        denom = reduced.denominator
        temp_denom = denom
        
        # 检查是否只包含2和5的因子
        while temp_denom % 2 == 0:
            temp_denom //= 2
        while temp_denom % 5 == 0:
            temp_denom //= 5
        
        is_terminating = temp_denom == 1
        
        if is_terminating:
            # 有限小数
            decimal_result = float(reduced)
            steps.append(FractionStep(
                description=f"分母只含2和5的因子，为有限小数：{decimal_result}",
                operation="转为有限小数",
                result=str(decimal_result),
                formula="小数= 分子/分母"
            ))
        else:
            # 循环小数，按精度截断
            decimal_result = round(float(reduced), problem.precision)
            steps.append(FractionStep(
                description=f"分母含其他质因数，为循环小数，按精度{problem.precision}截断：{decimal_result}",
                operation="转为循环小数",
                result=str(decimal_result),
                formula="小数= 分子/分母"
            ))
        
        return FractionResult(
            success=True,
            result=decimal_result,
            steps=steps,
            step_count=len(steps),
            formula=f"分数转小数：{fraction} → {decimal_result}",
            validation=True
        )
    
    def _convert_to_percent(self, fraction: Fraction, steps: list, problem: FractionProblem) -> FractionResult:
        """转换为百分数"""
        # 使用精确的分数计算避免浮点数精度问题
        percent_fraction = fraction * 100
        percent_value = float(percent_fraction)
        
        # 检查是否为整数百分数
        if percent_value == int(percent_value):
            percent_value = int(percent_value)
        else:
            # 四舍五入到合理精度
            percent_value = round(percent_value, 6)
            if percent_value == int(percent_value):
                percent_value = int(percent_value)
        
        steps.append(FractionStep(
            description=f"分数转百分数：{fraction} × 100 = {percent_value}%",
            operation="分数转百分数",
            result=f"{percent_value}%",
            formula="百分数 = ( (分子/分母) × 100 ）%"
        ))
        
        return FractionResult(
            success=True,
            result=f"{percent_value}",
            steps=steps,
            step_count=len(steps),
            formula=f"分数转百分数：{fraction} → {percent_value}%",
            validation=True
        )
    
    def _convert_to_latex(self, fraction: Fraction, steps: list, problem: FractionProblem) -> FractionResult:
        """转换为LaTeX格式"""
        from ..base_types import FractionUtils
        
        latex_result = FractionUtils.fraction_to_latex(fraction, problem.display_mixed)
        
        steps.append(FractionStep(
            description=f"转换为LaTeX格式：{fraction} → {latex_result}",
            operation="调整分数格式",
            result=latex_result
        ))
        
        return FractionResult(
            success=True,
            result=latex_result,
            steps=steps,
            step_count=len(steps),
            formula=f"调整分数格式：{fraction} → {latex_result}",
            validation=True
        )
