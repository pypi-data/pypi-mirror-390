"""
混合运算基础类型定义
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class OperationType(Enum):
    """运算类型"""
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    PARENTHESES = "()"
    EXPRESSION = "expression"


class NumberType(Enum):
    """数值类型"""
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"


@dataclass
class MixedOperand:
    """混合运算操作数"""
    value: Union[int, float, Decimal]
    original: str  # 原始输入
    number_type: NumberType
    position: int = 0  # 在表达式中的位置


@dataclass
class MixedStep:
    """混合运算步骤"""
    description: str
    operation: str
    inputs: List[str] = None
    result: str = ""
    formula: str = ""
    validation: bool = True
    meta: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.meta is None:
            self.meta = {}
    def __str__(self):
        return f"{self.description}: 结果： {self.result}"
    def to_dict(self) -> Dict[str, Any]:
        result = self.result
        return {
            "description": self.description,
            "operation": self.operation,
            "result": result,
            "formula": self.formula
        }


@dataclass
class MixedProblem:
    """混合运算问题"""
    expression: str
    operands: List[MixedOperand]
    operations: List[str]
    has_parentheses: bool = False
    complexity_level: int = 1  # 复杂度等级 1-5
    special_numbers: List[int] = None  # 特殊数字(0,1)的位置
    
    def __post_init__(self):
        if self.special_numbers is None:
            self.special_numbers = []


@dataclass
class MixedResult:
    """混合运算结果"""
    success: bool
    result: Union[str, int, float, Decimal] = None
    steps: List[MixedStep] = None
    step_count: int = 0
    formula: str = ""
    validation: bool = True
    error: str = ""
    technique_used: str = ""  # 使用的技巧
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        self.step_count = len(self.steps)


class MixedUtils:
    """混合运算工具类"""
    
    @staticmethod
    def is_special_number(num: Union[int, float]) -> bool:
        """判断是否为特殊数字"""
        return num in [0, 1, -1, 10, 100, 0.1, 0.5]
    
    @staticmethod
    def can_use_complement(a: Union[int, float], b: Union[int, float]) -> bool:
        """判断是否可以使用补数技巧"""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            # 检查是否能凑成整十、整百
            sum_val = a + b
            diff_val = abs(a - b)
            return (sum_val % 10 == 0 or sum_val % 100 == 0 or 
                    diff_val % 10 == 0 or diff_val % 100 == 0)
        return False
    
    @staticmethod
    def get_complement_strategy(a: Union[int, float], b: Union[int, float], op: str) -> Optional[Dict[str, Any]]:
        """获取补数策略"""
        if op == "+":
            if (a + b) % 10 == 0:
                return {"type": "sum_to_ten", "target": a + b}
            elif (a + b) % 100 == 0:
                return {"type": "sum_to_hundred", "target": a + b}
        elif op == "-":
            if abs(a - b) % 10 == 0:
                return {"type": "diff_to_ten", "target": abs(a - b)}
        return None
    
    @staticmethod
    def can_use_distribution(expr_parts: List[str]) -> bool:
        """判断是否可以使用分配律"""
        # 检查是否有 a*(b+c) 或 a*(b-c) 的模式
        for i, part in enumerate(expr_parts):
            if '*' in part and '(' in part:
                return True
        return False


class MixedCalculator(ABC):
    """混合运算算子基类"""
    
    def __init__(self, name: str, description: str, priority: int = 10):
        self.name = name
        self.description = description
        self.priority = priority
    
    @abstractmethod
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """
        判断是否匹配当前算子
        
        Returns:
            {
                "matched": bool,
                "score": float,  # 匹配分数 0-1
                "reason": str    # 匹配原因
            }
        """
        pass
    
    @abstractmethod
    def solve(self, problem: MixedProblem) -> MixedResult:
        """
        执行计算
        
        Args:
            problem: 混合运算问题
            
        Returns:
            MixedResult: 计算结果
        """
        pass
