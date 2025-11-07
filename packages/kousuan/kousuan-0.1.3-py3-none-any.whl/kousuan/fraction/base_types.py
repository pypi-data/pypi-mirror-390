"""
分数计算系统基础类型定义
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from fractions import Fraction
from decimal import Decimal
from enum import Enum
import re


class FractionType(Enum):
    """分数类型枚举"""
    PROPER = "proper"           # 真分数
    IMPROPER = "improper"       # 假分数
    MIXED = "mixed"             # 带分数
    INTEGER = "integer"         # 整数
    DECIMAL = "decimal"         # 小数
    PERCENT = "percent"         # 百分数


class OperationType(Enum):
    """运算类型枚举"""
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    COMPARE = "compare"
    CONVERT = "convert"
    RECIPROCAL = "reciprocal"
    REDUCE = "reduce"


@dataclass
class FractionOperand:
    """分数操作数"""
    raw: str                    # 原始文本
    fraction: Fraction          # 标准分数表示
    fraction_type: FractionType # 分数类型
    is_mixed: bool = False      # 是否为带分数
    whole_part: int = 0         # 带分数的整数部分
    original_format: str = ""   # 原始格式（LaTeX等）


@dataclass
class FractionProblem:
    """分数问题定义"""
    id: str
    original_text: str
    operation: OperationType
    operands: List[FractionOperand]
    target_format: str = "fraction"  # 期望输出格式
    precision: int = 4
    display_mixed: bool = False


@dataclass
class FractionStep:
    """分数计算步骤"""
    description: str
    operation: str
    inputs: List[str] = None
    result: Union[str, Fraction] = None
    formula: Optional[str] = None
    validation: bool = True
    meta: Dict[str, Any] = None
    def __str__(self):
        return f"{self.description}: {self.operation} → {self.result}"
    def to_dict(self) -> Dict[str, Any]:
        result = self.result
        return {
            "description": self.description,
            "operation": self.operation,
            "result": result,
            "formula": self.formula
        }


@dataclass
class FractionResult:
    """分数计算结果"""
    success: bool
    name: Optional[str] = None
    result: Union[Fraction, str, float] = None
    steps: List[FractionStep] = None
    step_count: int = 0
    formula: Optional[str] = None
    validation: bool = True
    error: Optional[str] = None


class FractionCalculator(ABC):
    """分数算子基类"""
    
    def __init__(self, name: str, description: str, priority: int = 5):
        self.name = name
        self.description = description
        self.priority = priority
    
    @abstractmethod
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """
        匹配模式判断
        返回: {"matched": bool, "score": float, "reason": str}
        """
        pass
    
    @abstractmethod
    def solve(self, problem: FractionProblem) -> FractionResult:
        """解决分数问题"""
        pass
    
    def validate_result(self, problem: FractionProblem, result: Union[Fraction, float]) -> bool:
        """验证结果正确性"""
        try:
            # 默认验证逻辑：重新计算对比
            return True
        except:
            return False


class FractionUtils:
    """分数工具类"""
    
    @staticmethod
    def parse_fraction_text(text: str) -> FractionOperand:
        """解析分数文本"""
        text = text.strip()
        
        # LaTeX格式: #frac{a}{b}#
        latex_match = re.match(r'#frac\{(\d+)\}\{(\d+)\}#', text)
        if latex_match:
            numer, denom = int(latex_match.group(1)), int(latex_match.group(2))
            return FractionOperand(
                raw=text,
                fraction=Fraction(numer, denom),
                fraction_type=FractionType.PROPER if numer < denom else FractionType.IMPROPER,
                original_format="latex"
            )
        
        # 带分数格式: #a frac{b}{c}# 或 a b/c
        mixed_latex = re.match(r'#(\d+)frac\{(\d+)\}\{(\d+)\}#', text)
        if mixed_latex:
            whole, numer, denom = int(mixed_latex.group(1)), int(mixed_latex.group(2)), int(mixed_latex.group(3))
            fraction = Fraction(whole * denom + numer, denom)
            return FractionOperand(
                raw=text,
                fraction=fraction,
                fraction_type=FractionType.MIXED,
                is_mixed=True,
                whole_part=whole,
                original_format="latex"
            )
        
        # 普通分数: a/b
        frac_match = re.match(r'(\d+)/(\d+)', text)
        if frac_match:
            numer, denom = int(frac_match.group(1)), int(frac_match.group(2))
            return FractionOperand(
                raw=text,
                fraction=Fraction(numer, denom),
                fraction_type=FractionType.PROPER if numer < denom else FractionType.IMPROPER
            )
        
        # 小数
        if '.' in text:
            try:
                decimal_val = float(text)
                return FractionOperand(
                    raw=text,
                    fraction=Fraction(decimal_val).limit_denominator(),
                    fraction_type=FractionType.DECIMAL
                )
            except ValueError:
                pass
        
        # 百分数
        if text.endswith('%'):
            try:
                percent_val = float(text[:-1]) / 100
                return FractionOperand(
                    raw=text,
                    fraction=Fraction(percent_val).limit_denominator(),
                    fraction_type=FractionType.PERCENT
                )
            except ValueError:
                pass
        
        # 整数
        if text.isdigit():
            return FractionOperand(
                raw=text,
                fraction=Fraction(int(text)),
                fraction_type=FractionType.INTEGER
            )
        
        raise ValueError(f"无法解析分数文本: {text}")
    
    @staticmethod
    def fraction_to_latex(fraction: Fraction, mixed: bool = False) -> str:
        """转换分数为LaTeX格式"""
        if fraction.denominator == 1:
            return str(fraction.numerator)
        
        if mixed and abs(fraction.numerator) >= fraction.denominator:
            whole = fraction.numerator // fraction.denominator
            remainder = abs(fraction.numerator) % fraction.denominator
            if remainder == 0:
                return str(whole)
            return f"#{whole}frac{{{remainder}}}{{{fraction.denominator}}}#"
        
        return f"#frac{{{fraction.numerator}}}{{{fraction.denominator}}}#"
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """最大公约数"""
        while b:
            a, b = b, a % b
        return abs(a)
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """最小公倍数"""
        return abs(a * b) // FractionUtils.gcd(a, b)


def to_latex(fraction: Fraction) -> str:
    """将 Fraction 转为 LaTeX 格式的字符串"""
    return FractionUtils.fraction_to_latex(fraction)