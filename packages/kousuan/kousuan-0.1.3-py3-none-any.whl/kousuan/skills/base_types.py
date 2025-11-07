"""
基础类型定义
包含Formula、FormulaElement、MathCalculator等核心类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from fractions import Fraction


class ElementType(Enum):
    """元素类型枚举"""
    NUMBER = "number"
    OPERATOR = "operator"
    BRACKET = "bracket"


class OperatorType(Enum):
    """运算符类型枚举"""
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POWER = "**"
    COMPARE_EQ = "=="
    COMPARE_GT = ">"
    COMPARE_LT = "<"
    COMPARE_GE = ">="
    COMPARE_LE = "<="


class NumberType(Enum):
    """数字类型枚举"""
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"


@dataclass
class FormulaElement:
    """算式元素"""
    type: ElementType
    value: Union[str, int, float, Fraction]
    number_type: Optional[NumberType] = None
    
    def __post_init__(self):
        """初始化后处理，自动识别数字类型"""
        if self.type == ElementType.NUMBER and self.number_type is None:
            self.number_type = self._detect_number_type()
    
    def _detect_number_type(self) -> NumberType:
        """自动检测数字类型"""
        if isinstance(self.value, int):
            return NumberType.INTEGER
        elif isinstance(self.value, float):
            return NumberType.DECIMAL
        elif isinstance(self.value, Fraction):
            return NumberType.FRACTION
        elif isinstance(self.value, str):
            # 尝试解析字符串
            if '/' in self.value:
                return NumberType.FRACTION
            elif '.' in self.value:
                return NumberType.DECIMAL
            else:
                return NumberType.INTEGER
        return NumberType.INTEGER
    
    def get_numeric_value(self) -> Union[int, float, Fraction]:
        """获取数值"""
        if isinstance(self.value, (int, float, Fraction)):
            return self.value
        elif isinstance(self.value, str):
            if self.number_type == NumberType.FRACTION:
                if '/' in self.value:
                    parts = self.value.split('/')
                    return Fraction(int(parts[0]), int(parts[1]))
                else:
                    return Fraction(int(self.value))
            elif self.number_type == NumberType.DECIMAL:
                return float(self.value)
            else:
                return int(self.value)
        return 0


@dataclass
class Formula:
    """数学算式类"""
    
    def __init__(self, type: str = "unknown", elements: List[FormulaElement] = None, answer: Union[str, int, float, Fraction] = None, scale_factors: List[float] = None):
        self.type = type
        self.answer = answer
        self.elements = elements or []
        self.scale_factors = scale_factors or [1.0]
        self.original_expression = self._reconstruct_original_expression()
    
    def _reconstruct_original_expression(self) -> str:
        """重构原始表达式（用于显示）"""
        if not self.elements:
            return ""
        parts = [str(elem.value) for elem in self.elements]
        if self.answer is not None:
            parts.append(f"={self.answer}")
        
        return ''.join(parts)

    def get_numbers(self) -> List[FormulaElement]:
        """获取所有数字元素"""
        return [elem for elem in self.elements if elem.value != '' and elem.type == ElementType.NUMBER]
    
    def get_operators(self) -> List[FormulaElement]:
        """获取所有运算符元素"""
        return [elem for elem in self.elements if elem.type == ElementType.OPERATOR]
    
    def to_expression(self) -> str:
        """转换为表达式字符串"""
        expr_parts = []
        for elem in self.elements:
            if elem.value == '×':
                expr_parts.append('*')
            elif elem.value == '÷':
                expr_parts.append('/')
            else:
                expr_parts.append(str(elem.value))
        return ' '.join(expr_parts)
    
    def evaluate_direct(self) -> Union[int, float, Fraction]:
        """直接计算结果（用于验证）"""
        expr = self.to_expression()
        # 处理分数
        expr = self._convert_fractions_for_eval(expr)
        try:
            return eval(expr)
        except:
            return 0
    
    def _convert_fractions_for_eval(self, expr: str) -> str:
        """转换分数表达式为可eval的形式"""
        # 简单处理，将 a/b 转换为 Fraction(a,b)
        fraction_pattern = r'(\d+)/(\d+)'
        expr = re.sub(fraction_pattern, r'Fraction(\1,\2)', expr)
        return expr
    
    def is_valid_expression(self) -> bool:
        """检查表达式是否有效"""
        if not self.elements:
            return False
        
        # 检查是否有数字
        numbers = self.get_numbers()
        if not numbers:
            return False
        
        # 检查数字是否都能转换为数值
        try:
            for num in numbers:
                num.get_numeric_value()
            return True
        except:
            return False


@dataclass
class CalculationStep:
    """计算步骤"""
    description: str  # 步骤描述
    operation: str   # 操作说明
    result: Union[int, float, Fraction, str]  # 步骤结果
    formula: Optional[str] = None  # 相关公式
    def __str__(self):
        return f"{self.description}: 结果： {self.result}"
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "operation": self.operation,
            "result": str(self.result),
            "formula": self.formula
        }


class MathCalculator(ABC):
    """速算算子基类"""
    
    def __init__(self, name: str, description: str, priority: int = 1, formula: str = ''):
        self.name = name
        self.description = description
        self.priority = priority
        self.formula = formula
    
    @abstractmethod
    def is_match_pattern(self, formula: Formula) -> bool:
        """判断算式是否匹配当前算子"""
        pass
    
    @abstractmethod
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建算法步骤"""
        pass
    def describe(self) -> str:
        """描述算子信息"""
        content = f"方法：{self.name} 描述：{self.description}"
        if self.formula:
            content += f" 公式：{self.formula}"
        return content
    def execute(self, formula: Formula) -> Tuple[Union[int, float, Fraction], List[CalculationStep]]:
        """执行算法步骤"""
        if not self.is_match_pattern(formula):
            raise ValueError(f"Formula doesn't match pattern for {self.name}")
        val = formula.evaluate_direct()
        formula_answer = str(formula.answer).strip() if formula.answer is not None else ""
        steps = self.construct_steps(formula)
        
        # 执行最后一步获取结果
        if steps:#
            result = steps[-1].result
            if isinstance(result, str) and '······' in result:
                ss = result.split('······')
                result = ss[0].strip() if formula_answer[0] == '@' else ss[1].strip()
            # 确保结果是数值类型
            elif isinstance(result, str):
                try:
                    # 尝试转换字符串为数值
                    if '.' in result:
                        result = float(result)
                    else:
                        result = int(result)
                except ValueError:
                    # 如果无法转换，使用直接计算结果
                    result = formula.evaluate_direct()
            return result, steps
        else:
            return val, []
    
    def validate(self, formula: Formula) -> bool:
        """检查算法步骤的结果是否和直接计算相匹配"""
        try:
            calculated_result, _ = self.execute(formula)
            direct_result = formula.evaluate_direct()
            
            # 处理不同类型的比较
            if isinstance(calculated_result, Fraction) and isinstance(direct_result, (int, float)):
                return abs(float(calculated_result) - float(direct_result)) < 1e-10
            elif isinstance(direct_result, Fraction) and isinstance(calculated_result, (int, float)):
                return abs(float(direct_result) - float(calculated_result)) < 1e-10
            else:
                return abs(float(calculated_result) - float(direct_result)) < 1e-10
        except:
            return False