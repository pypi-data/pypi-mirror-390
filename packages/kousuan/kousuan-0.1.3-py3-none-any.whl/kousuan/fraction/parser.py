"""
分数表达式解析器
"""

import re
from typing import List, Optional
from .base_types import FractionProblem, FractionOperand, OperationType, FractionUtils


class FractionParser:
    """分数表达式解析器"""
    
    @staticmethod
    def parse(expression: str) -> FractionProblem:
        """解析分数表达式"""
        expression = expression.strip()

        ## 表达式兼容处理
        expression = expression.replace(r'$\frac{', r'#frac{').replace(r'}$', r'}#')
        if re.search(r'#frac\{[\d\-]+\}\{[\d\-]+\}(?=[^#])', expression):
            expression = re.sub(r'#frac\{([\d\-]+)\}\{([\d\-]+)\}(?=[^#])', r'#frac{\1}{\2}#', expression)
        
        # 检查表达式是否包含分数格式
        if not FractionParser._has_fraction_format(expression) and ':' not in expression:
            raise ValueError(f"表达式不包含分数格式: {expression}")
        
        # 识别运算类型和操作数 - 调整@符号的处理优先级
        if ':' in expression:
            # 查看是否有两个：
            if expression.count(':') == 2 and '@' in expression:
                problem = FractionParser._parse_ratio_equation(expression)
                problem.id = "ratio_equation"
                return problem
            # a:b=@ 结构，直接转比值转数值问题
            if '=' in expression and '=@' in expression:
                left, right = expression.split('=')
                left_parts = [p.strip() for p in left.split(':')]
                if len(left_parts) == 2:
                    # 构造结构化问题
                    from fractions import Fraction
                    from .base_types import FractionOperand, FractionType
                    op1 = FractionUtils.parse_fraction_text(left_parts[0])
                    op2 = FractionUtils.parse_fraction_text(left_parts[1])
                    op3 = FractionOperand(
                        raw='@',
                        fraction=Fraction(0, 1),
                        fraction_type=FractionType.INTEGER,
                        original_format="unknown"
                    )
                    op3.__dict__['is_unknown'] = True   
                    operands = [op1, op2, op3]
                    return FractionProblem(
                        id="ratio_to_value",
                        original_text=expression,
                        operation=OperationType.CONVERT,
                        operands=operands
                    )
            return FractionParser._parse_convert(expression.split('=')[0])
        if '=' in expression and '@' in expression:
            return FractionParser._parse_equation(expression)
        elif '@' in expression:  # 添加@符号比较的处理
            return FractionParser._parse_comparison(expression)
        elif any(op in expression for op in ['>', '<', '≥', '≤']):
            return FractionParser._parse_comparison(expression)
        elif '+' in expression:
            return FractionParser._parse_addition(expression)
        elif '-' in expression:
            return FractionParser._parse_subtraction(expression)
        elif '×' in expression or '*' in expression:
            return FractionParser._parse_multiplication(expression)
        elif '÷' in expression or '/' in expression:
            return FractionParser._parse_division(expression)
        else:
            return FractionParser._parse_single_operand(expression)
    
    @staticmethod
    def _has_fraction_format(expression: str) -> bool:
        """检查表达式是否包含分数格式"""
        # 检查LaTeX分数格式
        if re.search(r'#[\d\-]*frac\{[\d@]+\}', expression):
            return True
        # 检查普通分数格式（但要确保不是纯整数）
        if re.search(r'\d+/\d+', expression):
            return True
        # 检查带分数格式
        if re.search(r'#\d+frac\{\d+\}\{\d+\}#', expression):
            return True
        # 如果只包含整数和运算符，不认为是分数表达式
        if re.match(r'^[\d\s+\-×*/÷()]+$', expression):
            return False
        return False
    
    @staticmethod
    def _parse_equation(expression: str) -> FractionProblem:
        """解析等式（包含@的题目）"""
        left, right = expression.split('=')
        left_parts = FractionParser._extract_operands(left)
        
        # 确定运算类型
        if '+' in left:
            operation = OperationType.ADD
        elif '-' in left:
            operation = OperationType.SUBTRACT
        elif '×' in left or '*' in left:
            operation = OperationType.MULTIPLY
        elif '÷' in left or '/' in left:
            operation = OperationType.DIVIDE
        else:
            operation = OperationType.CONVERT
        
        # 解析操作数
        operands = []
        for part in left_parts:
            if part != '@' and not part in ['+', '-', '×', '*', '÷', '/', ':']:
                try:
                    operands.append(FractionUtils.parse_fraction_text(part))
                except ValueError:
                    # 跳过无法解析的部分
                    continue
        
        # 确定目标格式
        target_format = "fraction"
        if '#frac{@}{@}#' in right:
            target_format = "latex_fraction"
        elif '@%' in right:
            target_format = "percent"
        elif '@' in right and '.' in right:
            target_format = "decimal"
        
        return FractionProblem(
            id="equation",
            original_text=expression,
            operation=operation,
            operands=operands,
            target_format=target_format
        )
    
    @staticmethod
    def _parse_comparison(expression: str) -> FractionProblem:
        """解析比较表达式"""
        # 先处理@符号的比较
        if '@' in expression:
            left, right = expression.split('@')
            operands = [
                FractionUtils.parse_fraction_text(left.strip()),
                FractionUtils.parse_fraction_text(right.strip())
            ]
            return FractionProblem(
                id="comparison",
                original_text=expression,
                operation=OperationType.COMPARE,
                operands=operands
            )
        
        # 然后处理传统的比较符号
        for op in ['≥', '≤', '>', '<']:
            if op in expression:
                left, right = expression.split(op)
                operands = [
                    FractionUtils.parse_fraction_text(left.strip()),
                    FractionUtils.parse_fraction_text(right.strip())
                ]
                return FractionProblem(
                    id="comparison",
                    original_text=expression,
                    operation=OperationType.COMPARE,
                    operands=operands
                )
        
        raise ValueError(f"无法解析比较表达式: {expression}")
    
    @staticmethod
    def _parse_addition(expression: str) -> FractionProblem:
        """解析加法表达式"""
        parts = expression.split('+')
        operands = []
        for part in parts:
            try:
                operands.append(FractionUtils.parse_fraction_text(part.strip()))
            except ValueError:
                # 跳过无法解析的部分
                continue
        
        if len(operands) < 2:
            raise ValueError(f"加法表达式需要至少两个操作数: {expression}")
        
        return FractionProblem(
            id="addition",
            original_text=expression,
            operation=OperationType.ADD,
            operands=operands
        )
    
    @staticmethod
    def _parse_subtraction(expression: str) -> FractionProblem:
        """解析减法表达式"""
        parts = expression.split('-')
        operands = []
        for part in parts:
            if part.strip():
                try:
                    operands.append(FractionUtils.parse_fraction_text(part.strip()))
                except ValueError:
                    continue
        
        if len(operands) < 2:
            raise ValueError(f"减法表达式需要至少两个操作数: {expression}")
        
        return FractionProblem(
            id="subtraction",
            original_text=expression,
            operation=OperationType.SUBTRACT,
            operands=operands
        )
    
    @staticmethod
    def _parse_multiplication(expression: str) -> FractionProblem:
        """解析乘法表达式"""
        for op in ['×', '*']:
            if op in expression:
                parts = expression.split(op)
                operands = []
                for part in parts:
                    try:
                        operands.append(FractionUtils.parse_fraction_text(part.strip()))
                    except ValueError:
                        continue
                
                if len(operands) < 2:
                    raise ValueError(f"乘法表达式需要至少两个操作数: {expression}")
                
                return FractionProblem(
                    id="multiplication", 
                    original_text=expression,
                    operation=OperationType.MULTIPLY,
                    operands=operands
                )
        
        raise ValueError(f"无法解析乘法表达式: {expression}")
    
    @staticmethod
    def _parse_division(expression: str) -> FractionProblem:
        """解析除法表达式"""
        for op in ['÷', '/']:
            if op in expression:
                parts = expression.split(op)
                operands = []
                for part in parts:
                    try:
                        operands.append(FractionUtils.parse_fraction_text(part.strip()))
                    except ValueError:
                        continue
                
                if len(operands) < 2:
                    raise ValueError(f"除法表达式需要至少两个操作数: {expression}")
                
                return FractionProblem(
                    id="division",
                    original_text=expression,
                    operation=OperationType.DIVIDE,
                    operands=operands
                )
        
        raise ValueError(f"无法解析除法表达式: {expression}")
    @staticmethod
    def _parse_ratio_equation(expression: str) -> FractionProblem:
        """解析比值等值方程 a:b = c:d，支持@未知数"""
        left, right = expression.split('=')
        left_parts = [p.strip() for p in left.split(':')]
        right_parts = [p.strip() for p in right.split(':')]
        if len(left_parts) != 2 or len(right_parts) != 2:
            raise ValueError(f"比值等值表达式格式错误: {expression}")
        operands = []
        for part in left_parts + right_parts:
            if part == '@':
                # 构造未知数操作数
                from fractions import Fraction
                from .base_types import FractionOperand, FractionType
                op = FractionOperand(
                    raw='@',
                    fraction=Fraction(0, 1),
                    fraction_type=FractionType.INTEGER,
                    original_format="unknown"
                )
                op.__dict__['is_unknown'] = True
                operands.append(op)
            else:
                op = FractionUtils.parse_fraction_text(part)
                operands.append(op)
        if len(operands) != 4:
            raise ValueError(f"比值等值表达式需要4个操作数: {expression}")
        return FractionProblem(
            id="ratio_equation",
            original_text=expression,
            operation=OperationType.CONVERT,
            operands=operands
        )
    @staticmethod
    def _parse_convert(expression: str) -> FractionProblem:
        """解析除法表达式"""
        for op in [':']:
            if op in expression:
                parts = expression.split(op)
                operands = []
                for part in parts:
                    try:
                        operands.append(FractionUtils.parse_fraction_text(part.strip()))
                    except ValueError:
                        continue
                
                if len(operands) < 2:
                    raise ValueError(f"除法表达式需要至少两个操作数: {expression}")
                
                return FractionProblem(
                    id="division",
                    original_text=expression,
                    operation=OperationType.CONVERT,
                    operands=operands
                )
        
        raise ValueError(f"无法解析除法表达式: {expression}")
    
    @staticmethod
    def _parse_single_operand(expression: str) -> FractionProblem:
        """解析单操作数（如约分、转换等）"""
        operand = FractionUtils.parse_fraction_text(expression)
        
        return FractionProblem(
            id="single",
            original_text=expression,
            operation=OperationType.REDUCE,
            operands=[operand]
        )
    
    @staticmethod
    def _extract_operands(expression: str) -> List[str]:
        """提取表达式中的操作数和运算符"""
        # 使用正则表达式分割，保留分隔符
        pattern = r'(#\d*frac\{\d+\}\{\d+\}#|\d+/\d+|\d+\.\d+|\d+%?|[@+\-×*/÷])'
        parts = re.findall(pattern, expression)
        return [part for part in parts if part.strip()]
