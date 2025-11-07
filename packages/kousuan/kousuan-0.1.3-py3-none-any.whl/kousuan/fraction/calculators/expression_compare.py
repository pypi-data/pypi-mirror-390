"""
运算后比较算子 - 先计算表达式结果再比较大小
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType
from ..parser import FractionParser


class ExpressionCompareCalculator(FractionCalculator):
    """运算后比较算子"""
    
    def __init__(self):
        super().__init__("运算后比较", "先计算表达式结果再比较大小", priority=5)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配运算后比较问题"""
        # 这个算子通常由引擎特别调用，处理复合表达式比较
        # 例如：1/3 + 1/2 @ 2/3
        if problem.operation == OperationType.COMPARE:
            # 检查是否有复合表达式（原始文本包含运算符）
            original = problem.original_text
            if any(op in original.split('@')[0] for op in ['+', '-', '×', '÷']):
                return {"matched": True, "score": 0.7, "reason": "运算后比较"}
        
        return {"matched": False, "score": 0.0, "reason": "不是运算后比较"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行运算后比较"""
        try:
            steps = []
            
            # 解析原始表达式的两侧
            original = problem.original_text
            if '@' not in original:
                raise ValueError("表达式格式错误")
            
            left_expr, right_expr = original.split('@')
            left_expr = left_expr.strip()
            right_expr = right_expr.strip()
            
            steps.append(FractionStep(
                description=f"需要比较：{left_expr} 与 {right_expr}",
                operation="识别比较表达式",
                result="先分别计算两侧的值"
            ))
            
            # 计算左侧表达式
            left_result = self._evaluate_expression(left_expr, steps)
            
            # 计算右侧表达式
            right_result = self._evaluate_expression(right_expr, steps)
            
            # 比较结果
            steps.append(FractionStep(
                description=f"比较计算结果：{left_result} 与 {right_result}",
                operation="比较结果",
                result="使用分数比较方法"
            ))
            
            # 执行比较
            if left_result > right_result:
                comparison = ">"
                explanation = f"因为 {left_result} > {right_result}"
            elif left_result < right_result:
                comparison = "<"
                explanation = f"因为 {left_result} < {right_result}"
            else:
                comparison = "="
                explanation = f"因为 {left_result} = {right_result}"
            
            steps.append(FractionStep(
                description=explanation,
                operation="得出结论",
                result=f"{left_expr} {comparison} {right_expr}",
                formula=f"{left_result} {comparison} {right_result}"
            ))
            
            return FractionResult(
                success=True,
                result=comparison,
                steps=steps,
                step_count=len(steps),
                formula=f"运算后比较：{left_expr} {comparison} {right_expr}",
                validation=True
            )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"运算后比较失败: {str(e)}"
            )
    
    def _evaluate_expression(self, expr: str, steps: list) -> Fraction:
        """计算表达式的值"""
        try:
            # 简单解析和计算表达式
            if '+' in expr:
                parts = expr.split('+')
                fractions = [self._parse_fraction(part.strip()) for part in parts]
                result = sum(fractions, Fraction(0))
                
                steps.append(FractionStep(
                    description=f"计算 {expr} = {' + '.join(str(f) for f in fractions)} = {result}",
                    operation="计算加法",
                    result=str(result)
                ))
                
            elif '-' in expr:
                parts = expr.split('-')
                fractions = [self._parse_fraction(part.strip()) for part in parts if part.strip()]
                result = fractions[0] - sum(fractions[1:], Fraction(0))
                
                steps.append(FractionStep(
                    description=f"计算 {expr} = {result}",
                    operation="计算减法",
                    result=str(result)
                ))
                
            elif '×' in expr or '*' in expr:
                op = '×' if '×' in expr else '*'
                parts = expr.split(op)
                fractions = [self._parse_fraction(part.strip()) for part in parts]
                result = fractions[0]
                for f in fractions[1:]:
                    result *= f
                
                steps.append(FractionStep(
                    description=f"计算 {expr} = {result}",
                    operation="计算乘法",
                    result=str(result)
                ))
                
            elif '÷' in expr or '/' in expr:
                op = '÷' if '÷' in expr else '/'
                parts = expr.split(op)
                fractions = [self._parse_fraction(part.strip()) for part in parts]
                result = fractions[0]
                for f in fractions[1:]:
                    result /= f
                
                steps.append(FractionStep(
                    description=f"计算 {expr} = {result}",
                    operation="计算除法",
                    result=str(result)
                ))
                
            else:
                # 单个分数
                result = self._parse_fraction(expr)
                
                steps.append(FractionStep(
                    description=f"解析分数 {expr} = {result}",
                    operation="解析分数",
                    result=str(result)
                ))
            
            return result
            
        except Exception as e:
            raise ValueError(f"无法计算表达式 {expr}: {str(e)}")
    
    def _parse_fraction(self, text: str) -> Fraction:
        """解析分数文本为Fraction对象"""
        from ..base_types import FractionUtils
        operand = FractionUtils.parse_fraction_text(text)
        return operand.fraction
