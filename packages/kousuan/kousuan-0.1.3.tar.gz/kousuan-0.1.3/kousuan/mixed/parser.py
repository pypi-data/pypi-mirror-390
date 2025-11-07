"""
混合运算表达式解析器
"""

import re
from typing import List, Tuple, Optional
from decimal import Decimal
from .base_types import MixedProblem, MixedOperand, NumberType, OperationType


class MixedParser:
    """混合运算解析器"""
    
    # 操作符优先级
    OPERATOR_PRECEDENCE = {
        '+': 1,
        '-': 1,
        '*': 2,
        '×': 2,
        '/': 2,
        '÷': 2,
        '(': 0,
        ')': 0
    }
    
    @classmethod
    def parse(cls, expression: str) -> MixedProblem:
        """
        解析混合运算表达式
        
        Args:
            expression: 表达式字符串
            
        Returns:
            MixedProblem: 解析后的问题对象
            
        Raises:
            ValueError: 当表达式格式错误时
        """
        # 输入验证
        if not expression or not expression.strip():
            raise ValueError("表达式不能为空")
        
        if '=' not in expression and '@' in expression:
            expression = re.sub(r'@([\d\-]+)', '=@', expression)
        eq_index = expression.find('=')
        answer = ""
        if eq_index != -1:
            # 处理等式，暂时只解析等号左侧
            expression = expression[:eq_index]
            answer_part = expression[eq_index + 1:]
            if answer_part and answer_part != '@' and answer_part != '?':
                answer = answer_part
        # 清理表达式
        expression = expression.replace(' ', '').replace('x', '*').replace('X', '*')
        # 标准化表达式
        normalized_expr = cls._normalize_expression(expression.strip())
        
        # 验证表达式格式
        cls._validate_expression(normalized_expr)
        
        # 检查括号
        has_parentheses = '(' in normalized_expr or ')' in normalized_expr
        
        # 提取操作数和操作符
        operands, operations = cls._extract_operands_and_operations(normalized_expr)
        
        # 验证解析结果
        if not operands:
            raise ValueError("表达式中没有找到有效的数字")
        
        # 计算复杂度等级
        complexity_level = cls._calculate_complexity(operands, operations, has_parentheses)
        
        # 查找特殊数字
        special_numbers = cls._find_special_numbers(operands)
        
        return MixedProblem(
            expression=normalized_expr,
            operands=operands,
            operations=operations,
            has_parentheses=has_parentheses,
            complexity_level=complexity_level,
            special_numbers=special_numbers
        )
    
    @classmethod
    def _normalize_expression(cls, expression: str) -> str:
        """标准化表达式"""
        # 移除空格
        expr = expression.replace(' ', '')
        
        # 统一运算符
        expr = expr.replace('×', '*').replace('÷', '/')
        
        # 处理负号 - 只在开头或括号后处理
        expr = re.sub(r'^-', '0-', expr)  # 开头的负号
        expr = re.sub(r'\(-', '(0-', expr)  # 括号后的负号
        
        return expr
    
    @classmethod
    def _validate_expression(cls, expression: str):
        """验证表达式格式"""
        # 检查是否包含无效字符
        valid_chars = set('0123456789+-*/.()×÷')
        invalid_chars = set(expression) - valid_chars
        if invalid_chars:
            raise ValueError(f"表达式包含无效字符: {', '.join(invalid_chars)}")
        
        # 检查括号匹配
        if not cls._check_parentheses_balance(expression):
            raise ValueError("括号不匹配")
        
        # 检查运算符连续
        if re.search(r'[+\-*/]{2,}', expression):
            raise ValueError("运算符不能连续出现")
        
        # 检查表达式开头和结尾
        if re.match(r'^[+*/]', expression):
            raise ValueError("表达式不能以 +, *, / 开头")
        
        if re.search(r'[+\-*/]$', expression):
            raise ValueError("表达式不能以运算符结尾")
    
    @classmethod
    def _check_parentheses_balance(cls, expression: str) -> bool:
        """检查括号是否匹配"""
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:  # 右括号多于左括号
                    return False
        return count == 0  # 最终应该平衡
    
    @classmethod
    def _extract_operands_and_operations(cls, expression: str) -> Tuple[List[MixedOperand], List[str]]:
        """提取操作数和操作符 - 简化版本，确保正确解析"""
        operands = []
        operations = []
        
        # 使用更简单的方法：逐字符解析
        i = 0
        current_number = ""
        position = 0
        
        while i < len(expression):
            char = expression[i]
            
            if char.isdigit() or char == '.':
                current_number += char
            elif char in '+-*/()':
                # 保存当前数字
                if current_number:
                    try:
                        if '.' in current_number:
                            value = float(current_number)
                            number_type = NumberType.DECIMAL
                        else:
                            value = int(current_number)
                            number_type = NumberType.INTEGER
                        
                        operand = MixedOperand(
                            value=value,
                            original=current_number,
                            number_type=number_type,
                            position=position
                        )
                        operands.append(operand)
                        position += 1
                        current_number = ""
                    except ValueError:
                        raise ValueError(f"无法解析数字: {current_number}")
                
                # 保存运算符
                operations.append(char)
            
            i += 1
        
        # 保存最后一个数字
        if current_number:
            try:
                if '.' in current_number:
                    value = float(current_number)
                    number_type = NumberType.DECIMAL
                else:
                    value = int(current_number)
                    number_type = NumberType.INTEGER
                
                operand = MixedOperand(
                    value=value,
                    original=current_number,
                    number_type=number_type,
                    position=position
                )
                operands.append(operand)
            except ValueError:
                raise ValueError(f"无法解析数字: {current_number}")
        
        return operands, operations
    
    @classmethod
    def _is_number(cls, token: str) -> bool:
        """检查token是否为有效数字"""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    @classmethod
    def _calculate_complexity(cls, operands: List[MixedOperand], operations: List[str], has_parentheses: bool) -> int:
        """计算复杂度等级"""
        complexity = 1
        
        # 操作数数量影响复杂度
        if len(operands) > 3:
            complexity += 1
        if len(operands) > 5:
            complexity += 1
        
        # 运算类型影响复杂度
        has_multiply_divide = any(op in ['*', '/'] for op in operations if op not in ['(', ')'])
        has_add_subtract = any(op in ['+', '-'] for op in operations if op not in ['(', ')'])
        
        if has_multiply_divide and has_add_subtract:
            complexity += 1  # 混合运算
        
        # 括号增加复杂度
        if has_parentheses:
            complexity += 1
        
        # 小数增加复杂度
        if any(op.number_type == NumberType.DECIMAL for op in operands):
            complexity += 1
        
        return min(complexity, 5)  # 最大复杂度为5
    
    @classmethod
    def _find_special_numbers(cls, operands: List[MixedOperand]) -> List[int]:
        """查找特殊数字的位置"""
        special_positions = []
        for i, operand in enumerate(operands):
            if operand.value in [0, 1, -1, 10, 100, 0.1, 0.5]:
                special_positions.append(i)
        return special_positions
