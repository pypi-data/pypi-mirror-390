"""
乘除链求值算子 - 从左到右处理乘除运算
"""

import re
from typing import Dict, Any, List
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep


class MulDivLeftToRightCalculator(MixedCalculator):
    """乘除链求值算子"""
    
    def __init__(self):
        super().__init__("乘除链求值", "从左到右逐步执行乘除运算", priority=5)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配只包含乘除运算的表达式"""
        # 检查是否只包含乘除运算（无加减）
        has_multiply_divide = any(op in ['*', '/'] for op in problem.operations)
        has_add_subtract = any(op in ['+', '-'] for op in problem.operations if op not in ['(', ')'])
        
        # 纯乘除运算（包括单一乘法或除法）
        if has_multiply_divide and not has_add_subtract and not problem.has_parentheses:
            return {
                "matched": True,
                "score": 0.8,
                "reason": "纯乘除运算，可从左到右计算"
            }
        return {"matched": False, "score": 0.0, "reason": "不是纯乘除运算"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行乘除链计算（直接用解析后的 operands 和 operations）"""
        try:
            expression = problem.expression
            operands = problem.operands
            operations = problem.operations
            steps = []
            if not operands or len(operands) < 2:
                return MixedResult(success=False, error="表达式过短，无法进行乘除链计算")

            current_result = float(operands[0].value)
            steps.append(MixedStep(
                description="开始乘除链计算",
                operation="开始计算",
                inputs=[str(operands[0].original)],
                result=str(current_result),
                formula=f"初始值 = {operands[0].original}"
            ))
            op_idx = 0
            for i in range(1, len(operands)):
                while op_idx < len(operations) and operations[op_idx] in ['(', ')']:
                    op_idx += 1
                if op_idx >= len(operations):
                    break
                operator = operations[op_idx]
                operand = float(operands[i].value)
                old_result = current_result
                if operator == '*':
                    current_result = float(current_result) * operand
                    steps.append(MixedStep(
                        description="执行乘法",
                        operation="乘法",
                        inputs=[str(old_result), str(operand)],
                        result=str(current_result),
                        formula=f"{old_result} × {operand} = {current_result}"
                    ))
                elif operator == '/':
                    if operand == 0:
                        return MixedResult(success=False, error="除数不能为0")
                    current_result = float(current_result) / operand
                    if isinstance(current_result, float) and current_result.is_integer():
                        current_result = int(current_result)
                    steps.append(MixedStep(
                        description="执行除法",
                        operation="除法",
                        inputs=[str(old_result), str(operand)],
                        result=str(current_result),
                        formula=f"{old_result} ÷ {operand} = {current_result}"
                    ))
                op_idx += 1
            if isinstance(current_result, float) and current_result.is_integer():
                current_result = int(current_result)
            steps.append(MixedStep(
                description="乘除链计算完成",
                operation="计算完成",
                inputs=[expression],
                result=str(current_result),
                formula=f"{expression} = {current_result}".replace('/', '÷')
            ))
            return MixedResult(
                success=True,
                result=current_result,
                steps=steps,
                step_count=len(steps),
                formula=f"乘除链: {expression} = {current_result}".replace('/', '÷'),
                validation=True,
                technique_used="从左到右乘除"
            )
        except Exception as e:
            return MixedResult(success=False, error=f"乘除链计算失败: {str(e)}")
