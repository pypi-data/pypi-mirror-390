"""
含括号混合运算算子 - 处理复杂的含括号混合运算
"""

from typing import Dict, Any
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep


class BracketedMixEvaluator(MixedCalculator):
    """含括号混合运算算子"""
    
    def __init__(self):
        super().__init__("含括号混合运算", "处理包含括号与混合运算的表达式", priority=2)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配含括号且有混合运算的表达式"""
        if not problem.has_parentheses:
            return {"matched": False, "score": 0.0, "reason": "表达式不包含括号"}
        
        # 检查是否有混合运算（既有乘除又有加减）
        has_multiply_divide = any(op in ['*', '/'] for op in problem.operations)
        has_add_subtract = any(op in ['+', '-'] for op in problem.operations if op not in ['(', ')'])
        
        if problem.has_parentheses and (has_multiply_divide or has_add_subtract):
            complexity_bonus = min(problem.complexity_level * 0.1, 0.2)
            return {
                "matched": True,
                "score": 0.85 + complexity_bonus,
                "reason": "含括号的混合运算表达式"
            }
        
        return {"matched": False, "score": 0.0, "reason": "不是混合运算"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行含括号混合运算"""
        try:
            expression = problem.expression
            steps = []
            
            steps.append(MixedStep(
                description="识别含括号的混合运算，按括号优先、乘除优先的顺序处理",
                operation="识别含括号的混合运算",
                inputs=[expression],
                result="开始处理",
                formula="括号优先 → 乘除优先 → 加减从左到右"
            ))
            
            # 使用递归方法处理括号
            current_expr = expression
            step_count = 0
            
            # 持续处理直到没有括号
            while '(' in current_expr:
                # 找到最内层括号
                innermost = self._find_innermost_parentheses(current_expr)
                if not innermost:
                    break
                
                start, end, inner_expr = innermost
                
                steps.append(MixedStep(
                    description=f"处理最内层括号: ({inner_expr})",
                    operation="处理最内层括号",
                    inputs=[inner_expr],
                    result=inner_expr.replace('/', '÷'),
                    formula=f"计算 ({inner_expr})"
                ))
                
                # 计算括号内的表达式
                inner_result = self._evaluate_expression_without_parentheses(inner_expr)
                
                steps.append(MixedStep(
                    description=f"括号内计算结果: ({inner_expr}) = {inner_result}",
                    operation="括号内计算",
                    inputs=[inner_expr],
                    result=str(inner_result).replace('/', '÷'),
                    formula=f"({inner_expr}) = {inner_result}"
                ))
                
                # 替换括号内容
                current_expr = current_expr[:start] + str(inner_result) + current_expr[end+1:]
                step_count += 1
            
            # 处理剩余的无括号表达式
            if any(op in current_expr for op in ['+', '-', '*', '/']):
                final_result = self._evaluate_expression_without_parentheses(current_expr)
                
                steps.append(MixedStep(
                    description=f"处理剩余表达式: {current_expr} = {final_result}",
                    operation="处理剩余表达式",
                    inputs=[current_expr],
                    result=str(final_result).replace('/', '÷'),
                    formula=f"{current_expr} = {final_result}"
                ))
            else:
                final_result = eval(current_expr)
            
            return MixedResult(
                success=True,
                result=final_result,
                steps=steps,
                step_count=len(steps),
                formula=f"含括号混合运算: {expression} = {final_result}",
                validation=True,
                technique_used="括号优先+运算优先级"
            )
            
        except Exception as e:
            return MixedResult(
                success=False,
                error=f"含括号混合运算失败: {str(e)}"
            )
    
    def _find_innermost_parentheses(self, expression: str) -> tuple:
        """找到最内层括号"""
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
                    inner_expr = expression[start+1:i]
                    if '(' not in inner_expr:
                        return (start, i, inner_expr)
        
        return None
    
    def _evaluate_expression_without_parentheses(self, expr: str):
        """计算不含括号的表达式，遵循运算优先级"""
        # 简化版：使用 eval（实际应该用完整的表达式解析器）
        try:
            return eval(expr)
        except:
            # 如果 eval 失败，尝试手工解析
            return self._manual_evaluate(expr)
    
    def _manual_evaluate(self, expr: str):
        """手工计算表达式（运算优先级）"""
        # 先处理乘除
        import re
        
        # 处理乘除运算
        while '*' in expr or '/' in expr:
            # 找到第一个乘除运算
            mul_match = re.search(r'(\d*\.?\d+)\s*\*\s*(\d*\.?\d+)', expr)
            div_match = re.search(r'(\d*\.?\d+)\s*/\s*(\d*\.?\d+)', expr)
            
            if mul_match and (not div_match or mul_match.start() < div_match.start()):
                # 处理乘法
                a, b = float(mul_match.group(1)), float(mul_match.group(2))
                result = a * b
                expr = expr[:mul_match.start()] + str(result) + expr[mul_match.end():]
            elif div_match:
                # 处理除法
                a, b = float(div_match.group(1)), float(div_match.group(2))
                result = a / b
                expr = expr[:div_match.start()] + str(result) + expr[div_match.end():]
            else:
                break
        
        # 处理加减运算
        try:
            return eval(expr)
        except:
            return float(expr)
