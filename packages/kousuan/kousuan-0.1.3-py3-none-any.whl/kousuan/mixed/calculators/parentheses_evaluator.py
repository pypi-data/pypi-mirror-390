"""
括号优先算子 - 处理括号运算
"""

import re
from typing import Dict, Any
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep
from ..parser import MixedParser


class ParenthesesEvaluator(MixedCalculator):
    """括号优先算子"""
    
    def __init__(self):
        super().__init__("括号优先", "按从内到外的顺序处理括号运算", priority=1)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配含有括号的表达式"""
        if problem.has_parentheses:
            return {
                "matched": True,
                "score": 1.0,
                "reason": "表达式包含括号，需要优先处理"
            }
        return {"matched": False, "score": 0.0, "reason": "表达式不包含括号"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行括号运算"""
        try:
            expression = problem.expression
            steps = []
            step_count = 0
            
            # 找到并处理最内层括号
            while '(' in expression:
                # 找到最内层括号
                innermost_match = self._find_innermost_parentheses(expression)
                if not innermost_match:
                    break
                
                start, end, inner_expr = innermost_match
                inner_expr_format = inner_expr.replace('/', '÷')
                steps.append(MixedStep(
                    description=f"识别最内层括号",
                    operation="识别括号",
                    inputs=[inner_expr],
                    result=f"({inner_expr_format})",
                    formula=f"计算 ({inner_expr_format})"
                ))
                
                # 直接计算括号内的表达式（避免递归调用引擎）
                try:
                    inner_value = eval(inner_expr)
                    if isinstance(inner_value, float) and inner_value.is_integer():
                        inner_value = int(inner_value)
                        
                    steps.append(MixedStep(
                        description=f"计算括号内容",
                        operation="计算括号",
                        inputs=[inner_expr_format],
                        result=str(inner_value),
                        formula=f"({inner_expr_format}) = {inner_value}"
                    ))
                    
                    # 替换括号及其内容
                    expression = expression[:start] + str(inner_value) + expression[end+1:]
                    step_count += 1
                except Exception as e:
                    return MixedResult(
                        success=False,
                        error=f"括号内计算失败: {inner_expr_format}, 错误: {str(e)}"
                    )
            
            # 处理剩余的表达式（如果还有运算）
            if any(op in expression for op in ['+', '-', '*', '/']):
                try:
                    final_value = eval(expression)
                    if isinstance(final_value, float) and final_value.is_integer():
                        final_value = int(final_value)
                        
                    steps.append(MixedStep(
                        description=f"计算最终结果",
                        operation="最终计算",
                        inputs=[expression],
                        result=str(final_value),
                        formula=f"{expression} = {final_value}".replace('/', '÷')
                    ))
                    
                    return MixedResult(
                        success=True,
                        result=final_value,
                        steps=steps,
                        step_count=len(steps),
                        formula=f"括号优先: {problem.expression} = {final_value}".replace('/', '÷'),
                        validation=True,
                        technique_used="括号优先"
                    )
                except Exception as e:
                    return MixedResult(
                        success=False,
                        error=f"最终计算失败: {expression}, 错误: {str(e)}"
                    )
            else:
                # 没有剩余运算，直接返回
                try:
                    final_value = eval(expression)
                    if isinstance(final_value, float) and final_value.is_integer():
                        final_value = int(final_value)
                        
                    return MixedResult(
                        success=True,
                        result=final_value,
                        steps=steps,
                        step_count=len(steps),
                        formula=f"括号优先: {problem.expression} = {final_value}",
                        validation=True,
                        technique_used="括号优先"
                    )
                except Exception as e:
                    return MixedResult(
                        success=False,
                        error=f"最终计算失败: {expression}, 错误: {str(e)}"
                    )
            
        except Exception as e:
            return MixedResult(
                success=False,
                error=f"括号运算失败: {str(e)}"
            )
    
    def _find_innermost_parentheses(self, expression: str) -> tuple:
        """找到最内层括号"""
        # 从左到右找到第一个 '('，然后找到对应的 ')'
        depth = 0
        start = -1
        
        for i, char in enumerate(expression):
            if char == '(':
                if depth == 0:
                    start = i
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and start != -1:
                    # 找到了一对括号
                    inner_expr = expression[start+1:i]
                    # 检查这是否是最内层（不包含括号）
                    if '(' not in inner_expr:
                        return (start, i, inner_expr)
        
        return None
