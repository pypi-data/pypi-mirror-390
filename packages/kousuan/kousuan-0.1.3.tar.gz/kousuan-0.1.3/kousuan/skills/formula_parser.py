"""
算式解析器
负责将字符串表达式解析为Formula对象
"""

from typing import List, Tuple
import re
import math
from .base_types import Formula, FormulaElement, ElementType


class FormulaParser:
    """算式解析器"""
    
    @staticmethod
    def parse(expression: str) -> Formula:
        """解析表达式字符串为Formula对象"""
        if '=' not in expression and '@' in expression:
            expression = re.sub(r'@([\d\-]+)', '=@', expression)
        eq_index = expression.find('=')
        answer = ""
        if eq_index != -1:
            answer_part = expression[eq_index + 1:]
            # 处理等式，暂时只解析等号左侧
            expression = expression[:eq_index]
            if answer_part and answer_part != '@' and answer_part != '?':
                answer = answer_part
        # 清理表达式
        expression = expression.replace(' ', '').replace('x', '*').replace('X', '*')
        
        # 识别算式类型
        formula_type = FormulaParser._detect_formula_type(expression)
        
        # 分词
        elements = FormulaParser._tokenize(expression)
        
        # 清理无效小数点
        cleaned_elements = FormulaParser._clean_invalid_decimals(elements)

        return Formula(type=formula_type, elements=cleaned_elements, answer=answer)

    @staticmethod
    def _clean_invalid_decimals(elements: List[FormulaElement]) -> List[FormulaElement]:
        """清理无效的小数点，如106.0→106, 45.0→45"""
        cleaned_elements = []
        
        for elem in elements:
            if elem.type == ElementType.NUMBER and '.' in elem.value:
                try:
                    num_value = float(elem.value)
                    # 检查是否为整数值的小数表示
                    if num_value.is_integer():
                        # 转换为整数字符串
                        cleaned_value = str(int(num_value))
                        cleaned_elements.append(FormulaElement(ElementType.NUMBER, cleaned_value))
                    else:
                        # 保留真正的小数
                        cleaned_elements.append(elem)
                except ValueError:
                    # 如果无法转换，保持原样
                    cleaned_elements.append(elem)
            else:
                cleaned_elements.append(elem)
        
        return cleaned_elements
 
    

    
    @staticmethod
    def _detect_formula_type(expression: str) -> str:
        """检测算式类型"""
        if '+' in expression and '-' not in expression:
            return "addition"
        elif '-' in expression and '+' not in expression:
            return "subtraction"
        elif '*' in expression or '×' in expression:
            return "multiplication"
        elif '÷' in expression:
            return "division"
        elif '/' in expression:
            return "fraction"  # 保留"/"作为分数符号
        elif any(op in expression for op in ['==', '>', '<', '>=', '<=']):
            return "comparison"
        elif '+' in expression and '-' in expression:
            return "mixed_addition_subtraction"
        else:
            return "unknown"
    
    @staticmethod
    def _tokenize(expression: str) -> List[FormulaElement]:
        """分词解析"""
        elements = []
        current_token = ""
        
        i = 0
        while i < len(expression):
            char = expression[i]
            
            if char.isdigit() or char == '.':
                current_token += char
            elif char == '/':
                # 检查是否是分数
                if current_token and i + 1 < len(expression) and expression[i + 1].isdigit():
                    current_token += char
                else:
                    if current_token:
                        elements.append(FormulaElement(ElementType.NUMBER, current_token))
                        current_token = ""
                    elements.append(FormulaElement(ElementType.OPERATOR, char))
            elif char in '+-*×÷':
                if current_token:
                    elements.append(FormulaElement(ElementType.NUMBER, current_token))
                    current_token = ""
                elements.append(FormulaElement(ElementType.OPERATOR, char))
            elif char in '()':
                if current_token:
                    elements.append(FormulaElement(ElementType.NUMBER, current_token))
                    current_token = ""
                elements.append(FormulaElement(ElementType.BRACKET, char))
            elif char in '=<>':
                if current_token:
                    elements.append(FormulaElement(ElementType.NUMBER, current_token))
                    current_token = ""
                # 处理复合比较运算符
                if i + 1 < len(expression) and expression[i + 1] == '=':
                    elements.append(FormulaElement(ElementType.OPERATOR, char + '='))
                    i += 1
                else:
                    elements.append(FormulaElement(ElementType.OPERATOR, char))
            
            i += 1
        
        if current_token:
            elements.append(FormulaElement(ElementType.NUMBER, current_token))
        
        return elements