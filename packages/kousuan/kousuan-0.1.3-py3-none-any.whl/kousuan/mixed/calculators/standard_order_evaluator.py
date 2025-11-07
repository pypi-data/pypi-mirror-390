"""
标准无括号混合求值算子 - 按运算优先级处理混合运算
"""

import re
from typing import Dict, Any, List, Tuple
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep


class StandardOrderEvaluator(MixedCalculator):
    """标准无括号混合求值算子"""
    
    def __init__(self):
        super().__init__("标准混合运算", "按运算优先级处理无括号混合运算", priority=10)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配包含混合运算的无括号表达式"""
        has_multiply_divide = any(op in ['*', '/'] for op in problem.operations)
        has_add_subtract = any(op in ['+', '-'] for op in problem.operations if op not in ['(', ')'])
        # 只有同时有乘除和加减才算混合运算
        if (has_multiply_divide or has_add_subtract) and not problem.has_parentheses:
            return {
                "matched": True,
                "score": 0.8,
                "reason": "无括号混合运算，需按优先级处理"
            }
        return {"matched": False, "score": 0.0, "reason": "不是混合运算或包含括号"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行标准混合运算"""
        try:
            expression = problem.expression
            steps = []
            
            steps.append(MixedStep(
                description="开始混合运算",
                operation="识别优先级",
                inputs=[expression],
                result="识别运算优先级",
                formula="乘除优先级 > 加减优先级"
            ))
            
            # 使用Python的eval来确保正确的运算优先级，但记录步骤
            result_value = self._evaluate_with_steps(expression, steps)
            
            steps.append(MixedStep(
                description="混合运算完成",
                operation="计算完成",
                inputs=[expression],
                result=str(result_value),
                formula=f"{expression} = {result_value}"
            ))
            
            return MixedResult(
                success=True,
                result=result_value,
                steps=steps,
                step_count=len(steps),
                formula=f"混合运算: {expression} = {result_value}",
                validation=True,
                technique_used="运算优先级"
            )
            
        except Exception as e:
            return MixedResult(
                success=False,
                error=f"标准混合运算失败: {str(e)}"
            )
    
    def _evaluate_with_steps(self, expression: str, steps: List[MixedStep]) -> float:
        """按步骤计算表达式，确保正确的运算优先级"""
        
        # 先找到所有乘除运算并逐个处理
        current_expr = expression
        
        # 使用正则表达式匹配乘除运算（包括负数）
        mul_div_pattern = r'(-?\d*\.?\d+)\s*([*/])\s*(-?\d*\.?\d+)'
        
        while re.search(mul_div_pattern, current_expr):
            match = re.search(mul_div_pattern, current_expr)
            if not match:
                break
            
            full_match = match.group(0)
            left_operand = float(match.group(1))
            operator = match.group(2)
            right_operand = float(match.group(3))
            
            # 执行运算
            if operator == '*':
                result = left_operand * right_operand
                op_desc = "乘法"
                op_symbol = "×"
            else:  # operator == '/'
                if right_operand == 0:
                    raise ValueError("除数不能为0")
                result = left_operand / right_operand
                op_desc = "除法"
                op_symbol = "÷"
            
            # 格式化结果
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            steps.append(MixedStep(
                description=f"先算{op_desc}",
                operation=f"先算{op_desc}",
                inputs=[str(left_operand), str(right_operand)],
                result=str(result),
                formula=f"{left_operand} {op_symbol} {right_operand} = {result}"
            ))
            
            # 替换表达式中的这部分
            current_expr = current_expr.replace(full_match, str(result), 1)
        
        # 现在处理剩余的加减运算
        if re.search(r'[+\-]', current_expr):
            steps.append(MixedStep(
                description="继续处理加减",
                operation="处理加减",
                inputs=[current_expr],
                result="处理加减运算",
                formula="从左到右处理加减"
            ))
            
            # 计算加减表达式
            try:
                final_result = eval(current_expr)
                if isinstance(final_result, float) and final_result.is_integer():
                    final_result = int(final_result)
                
                # 如果有加减运算，记录步骤
                if '+' in current_expr or '-' in current_expr:
                    steps.append(MixedStep(
                        description="计算加减运算",
                        operation="加减运算",
                        inputs=[current_expr],
                        result=str(final_result),
                        formula=f"{current_expr} = {final_result}"
                    ))
                
                return final_result
            except Exception as e:
                raise ValueError(f"加减运算计算失败: {current_expr}")
        else:
            # 只剩一个数字
            return float(current_expr)
