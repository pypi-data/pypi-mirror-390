"""
单位换算基础类型定义
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from decimal import Decimal
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class UnitType(Enum):
    """单位类型枚举"""
    LENGTH = "length"           # 长度
    AREA = "area"              # 面积
    VOLUME = "volume"          # 体积
    TIME = "time"              # 时间
    MASS = "mass"              # 质量
    CURRENCY = "currency"      # 货币
    NUMBER = "number"          # 数字单位
    PERCENTAGE = "percentage"  # 百分比
    DISCOUNT = "discount"      # 折扣
    UNKNOWN = "unknown"        # 未知类型


@dataclass
class UnitValue:
    """单位值"""
    value: float
    unit: str
    operator: str = "+"
    
    def __str__(self):
        # 先判断value是否数值，如果self.value可以是整数，则显示为整数
        if not isinstance(self.value, (int, float)):
            return f"{self.value}{self.unit}"
        if abs(self.value - round(self.value)) < 1e-10:
            return f"{int(round(self.value))}{self.unit}"
        return f"{self.value}{self.unit}"

@dataclass
class ConversionStep:
    """单位换算步骤"""
    description: str
    operation: str
    from_value: UnitValue
    result: UnitValue  # 修改字段名以保持一致性
    formula: Optional[str] = None
    
    def __str__(self):
        return f"{self.description}: {self.from_value} → {self.result}"
    def to_dict(self) -> Dict[str, Any]:
        result = self.result
        if isinstance(result, UnitValue):
            result = f"{result.value}{result.unit}"
        return {
            "description": self.description,
            "operation": self.operation,
            "from_value": str(self.from_value),
            "result": result,
            "formula": self.formula
        }


@dataclass
class UnitProblem:
    """单位换算题目"""
    original_text: str
    unit_type: UnitType
    source_values: List[UnitValue]
    target_unit: str
    
    def __str__(self):
        return self.original_text


class UnitCalculator(ABC):
    """单位换算算子基类"""
    
    def __init__(self, name: str, description: str, unit_type: UnitType):
        self.name = name
        self.description = description
        self.unit_type = unit_type
        self.conversion_rules = self._initialize_conversion_rules()
    
    def _round_result(self, value: float, precision: int = 10) -> float:
        """使用Decimal进行高精度四舍五入"""
        try:
            # 使用Decimal进行高精度计算
            decimal_value = Decimal(str(value))
            # 四舍五入到指定精度
            rounded = round(float(decimal_value), precision)
            
            # 如果结果接近整数，返回整数
            if abs(rounded - round(rounded)) < 1e-10:
                return int(round(rounded))
            return rounded
        except:
            # 如果Decimal转换失败，使用普通四舍五入
            return round(value, precision)
    
    @abstractmethod
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化单位换算规则"""
        pass
    
    @abstractmethod
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否匹配当前算子"""
        pass
    
    @abstractmethod
    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解单位换算问题，返回(结果, 步骤列表)"""
        pass
    
    def get_conversion_factor(self, from_unit: str, to_unit: str) -> Optional[float]:
        """获取两个单位之间的换算因子"""
        if from_unit in self.conversion_rules:
            return self.conversion_rules[from_unit].get(to_unit)
        return None
    
    def validate_result(self, problem: UnitProblem, result: float) -> bool:
        """验证计算结果"""
        try:
            # 简单验证：重新计算一遍
            calculated_result, _ = self.solve(problem)
            return abs(calculated_result - result) < 1e-10
        except:
            return False
