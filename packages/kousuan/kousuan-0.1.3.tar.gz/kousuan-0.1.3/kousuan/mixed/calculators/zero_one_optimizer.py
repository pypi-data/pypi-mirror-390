"""
0/1优化算子 - 处理特殊数字的短路计算
"""

from typing import Dict, Any
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep


class ZeroOneOptimizer(MixedCalculator):
    """0/1优化算子"""
    
    def __init__(self):
        super().__init__("0/1优化", "处理包含0或1的特殊运算", priority=3)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配包含特殊数字的表达式"""
        if not problem.special_numbers:
            return {"matched": False, "score": 0.0, "reason": "不包含特殊数字0或1"}
        
        # 检查是否有0或1
        has_zero = False
        has_one = False
        for pos in problem.special_numbers:
            if pos < len(problem.operands):
                value = problem.operands[pos].value
                if value == 0:
                    has_zero = True
                elif value == 1:
                    has_one = True
        
        if not (has_zero or has_one):
            return {"matched": False, "score": 0.0, "reason": "不包含特殊数字0或1"}
        
        # 检查是否为简单的乘法链（不包含加减），才能用短路
        has_add_subtract = any(op in ['+', '-'] for op in problem.operations if op not in ['(', ')'])
        
        # 如果有0且是纯乘除表达式，可以短路
        if has_zero and not has_add_subtract:
            return {
                "matched": True,
                "score": 0.95,
                "reason": "包含0的纯乘除表达式，可短路优化"
            }
        
        # 如果有1且是纯乘除表达式，可以优化
        if has_one and not has_add_subtract:
            return {
                "matched": True,
                "score": 0.8,
                "reason": "包含1的纯乘除表达式，可优化"
            }
        
        return {"matched": False, "score": 0.0, "reason": "包含加减运算，不适用0/1短路优化"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行0/1优化（仅对乘0短路，其他情况正常计算）"""
        try:
            expression = problem.expression
            operands = problem.operands
            operations = problem.operations
            steps = []
            has_add_subtract = any(op in ['+', '-'] for op in operations if op not in ['(', ')'])
            if has_add_subtract:
                return MixedResult(success=False, error="包含加减运算的表达式不适用0/1短路优化")

            # 处理乘法中的0
            zero_multiply_pattern = self._find_zero_multiply(operands, operations)
            if zero_multiply_pattern:
                steps.append(MixedStep(
                    description="发现乘0短路",
                    operation="乘0短路",
                    inputs=[expression],
                    result="0",
                    formula="任何数 × 0 = 0",
                    meta={"technique": "0乘法短路"}
                ))
                return MixedResult(
                    success=True,
                    result=0,
                    steps=steps,
                    step_count=len(steps),
                    formula=f"{expression} = 0 (0乘法短路)",
                    validation=True,
                    technique_used="0乘法短路"
                )

            # 其他情况直接从左到右计算（不做1优化，保证链式运算）
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
            return MixedResult(success=False, error=f"0/1优化失败: {str(e)}")
    
    def _find_zero_multiply(self, operands, operations):
        """查找乘法中的0"""
        # 只在纯乘法表达式中查找0
        for i, operand in enumerate(operands):
            if operand.value == 0:
                # 检查这个0是否参与乘法
                if i > 0 and i - 1 < len(operations) and operations[i - 1] == '*':
                    return {"position": i, "operation_index": i - 1}
                if i < len(operations) and operations[i] == '*':
                    return {"position": i, "operation_index": i}
        return None
    
    def _find_one_multiply(self, operands, operations):
        """查找乘法中的1"""
        positions = []
        for i, operand in enumerate(operands):
            if operand.value == 1:
                # 检查这个1是否参与乘法
                has_multiply = False
                if i > 0 and i - 1 < len(operations) and operations[i - 1] == '*':
                    has_multiply = True
                if i < len(operations) and operations[i] == '*':
                    has_multiply = True
                
                if has_multiply:
                    positions.append(i)
        
        return positions
    
    def _remove_ones_from_expression(self, expression, operands, operations, one_positions):
        """从表达式中移除1"""
        # 简单的字符串替换方法
        result = expression
        
        # 替换 *1 和 1*
        result = result.replace('*1*', '*')  # 中间的1
        result = result.replace('*1', '')    # 末尾的1
        result = result.replace('1*', '')    # 开头的1
        
        # 处理边界情况
        if result.startswith('*'):
            result = '1' + result
        if result.endswith('*'):
            result = result + '1'
        if result == '':
            result = '1'
        
        return result
