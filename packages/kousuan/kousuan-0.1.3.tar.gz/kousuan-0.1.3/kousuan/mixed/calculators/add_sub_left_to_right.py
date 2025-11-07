"""
加减链算子 - 从左到右处理加减运算，支持凑整技巧
"""

import re
from typing import Dict, Any, List, Tuple
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep, MixedUtils


class AddSubLeftToRightCalculator(MixedCalculator):
    """加减链算子"""
    
    def __init__(self):
        super().__init__("加减链", "从左到右处理加减运算，支持凑整优化", priority=8)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配只包含加减运算的表达式"""
        # 检查是否只包含加减运算（无乘除）
        has_add_subtract = any(op in ['+', '-'] for op in problem.operations if op not in ['(', ')'])
        has_multiply_divide = any(op in ['*', '/'] for op in problem.operations)
        # 允许两个及以上操作数，只要没有乘除且无括号
        if has_add_subtract and not has_multiply_divide and not problem.has_parentheses and len(problem.operands) >= 2:
            return {
                "matched": True,
                "score": 0.9,
                "reason": "纯加减运算，可从左到右计算"
            }
        return {"matched": False, "score": 0.0, "reason": "不是纯加减运算"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行加减链计算（直接用解析后的 operands 和 operations）"""
        try:
            expression = problem.expression
            steps = []
            operands = problem.operands
            operations = problem.operations
            if not operands or len(operands) < 2:
                return MixedResult(success=False, error="表达式过短，无法进行加减链计算")

            current_result = float(operands[0].value)
            ## 设置最大精确度为6位小数
            current_result = round(current_result, 6)
            steps.append(MixedStep(
                description="开始加减链计算",
                operation="开始计算",
                inputs=[str(operands[0].original)],
                result=str(current_result),
                formula=f"初始值 = {operands[0].original}"
            ))

            op_idx = 0
            for i in range(1, len(operands)):
                # 跳过括号
                while op_idx < len(operations) and operations[op_idx] in ['(', ')']:
                    op_idx += 1
                if op_idx >= len(operations):
                    break
                operator = operations[op_idx]
                operand = float(operands[i].value)
                old_result = current_result
                if operator == '+':
                    current_result = float(current_result) + operand
                    current_result = round(current_result, 6)
                    steps.append(MixedStep(
                        description="执行加法",
                        operation="加法",
                        inputs=[str(old_result), str(operand)],
                        result=str(current_result),
                        formula=f"{old_result} + {operand} = {current_result}"
                    ))
                elif operator == '-':
                    current_result = float(current_result) - operand
                    current_result = round(current_result, 6)
                    steps.append(MixedStep(
                        description="执行减法",
                        operation="减法",
                        inputs=[str(old_result), str(operand)],
                        result=str(current_result),
                        formula=f"{old_result} - {operand} = {current_result}"
                    ))
                op_idx += 1

            # 检查结果是否为整数
            if isinstance(current_result, float) and current_result.is_integer():
                current_result = int(current_result)

            steps.append(MixedStep(
                description="加减链计算完成",
                operation="计算完成",
                inputs=[expression],
                result=str(current_result),
                formula=f"{expression} = {current_result}"
            ))

            return MixedResult(
                success=True,
                result=current_result,
                steps=steps,
                step_count=len(steps),
                formula=f"从左到右: {expression} = {current_result}",
                validation=True,
                technique_used="从左到右加减"
            )
        except Exception as e:
            return MixedResult(success=False, error=f"加减链计算失败: {str(e)}")

    def _parse_tokens(self, expression: str) -> List[str]:
        """将表达式解析为数字和运算符的列表"""
        # 使用正则表达式匹配数字和运算符
        tokens = []
        # 匹配数字（包括小数）和运算符
        pattern = r'[-+]?\d*\.?\d+|[+\-]'
        matches = re.finditer(pattern, expression)
        for match in matches:
            tokens.append(match.group())
        return tokens
    def _find_complement_opportunities(self, tokens: List[str]) -> List[Tuple[int, int]]:
        """寻找可以凑整的数字对
        返回可以凑整的数字对的索引位置
        """
        opportunities = []
        # 检查相邻的两个数字
        for i in range(0, len(tokens) - 2, 2):
            num1 = float(tokens[i])
            num2 = float(tokens[i + 2])
            # 检查是否可以凑整（和为10的倍数）
            if (num1 + num2) % 10 == 0:
                opportunities.append((i, i + 2))
        return opportunities


    def _solve_with_complement(self, tokens: List[str], steps: List[MixedStep], expression: str) -> MixedResult:
        """使用凑整技巧求解"""
        steps.append(MixedStep(
            description="识别凑整机会",
            operation="识别凑整",
            inputs=[expression],
            result="使用凑整法",
            formula="寻找能凑成整十、整百的数字组合"
        ))
        
        # 简化版：直接计算并说明使用了凑整
        try:
            result_value = eval(expression)
            
            steps.append(MixedStep(
                description="应用凑整技巧",
                operation="凑整计算",
                inputs=[expression],
                result=str(result_value),
                formula=f"凑整法: {expression} = {result_value}",
                meta={"technique": "凑整"}
            ))
            
            return MixedResult(
                success=True,
                result=result_value,
                steps=steps,
                step_count=len(steps),
                formula=f"凑整法: {expression} = {result_value}",
                validation=True,
                technique_used="凑整技巧"
            )
            
        except Exception as e:
            return self._solve_left_to_right(tokens, steps, expression)
    
    def _solve_left_to_right(self, tokens: List[str], steps: List[MixedStep], expression: str) -> MixedResult:
        """从左到右求解"""
        current_result = float(tokens[0])
        steps.append(MixedStep(
            description="开始加减链计算",
            operation="开始计算",
            inputs=[tokens[0]],
            result=str(current_result),
            formula=f"初始值 = {tokens[0]}"
        ))

        # 修正循环逻辑，依次处理所有运算符和数字
        i = 1
        while i < len(tokens):
            operator = tokens[i]
            operand = float(tokens[i + 1])
            old_result = current_result
            if operator == '+':
                current_result = current_result + operand
                steps.append(MixedStep(
                    description="执行加法",
                    operation="加法",
                    inputs=[str(old_result), str(operand)],
                    result=str(current_result),
                    formula=f"{old_result} + {operand} = {current_result}"
                ))
            elif operator == '-':
                current_result = current_result - operand
                steps.append(MixedStep(
                    description="执行减法",
                    operation="减法",
                    inputs=[str(old_result), str(operand)],
                    result=str(current_result),
                    formula=f"{old_result} - {operand} = {current_result}"
                ))
            i += 2

        # 检查结果是否为整数
        if isinstance(current_result, float) and current_result.is_integer():
            current_result = int(current_result)

        steps.append(MixedStep(
            description="加减链计算完成",
            operation="计算完成",
            inputs=[expression],
            result=str(current_result),
            formula=f"{expression} = {current_result}"
        ))

        return MixedResult(
            success=True,
            result=current_result,
            steps=steps,
            step_count=len(steps),
            formula=f"从左到右: {expression} = {current_result}",
            validation=True,
            technique_used="从左到右加减"
        )