"""
分数算子注册器
"""

from typing import List, Dict, Any, Optional
from .base_types import FractionCalculator, FractionProblem


class FractionCalculatorRegistry:
    from .calculators.ratio_to_value import RatioToValueCalculator
    # 移除类体 import，改为方法体 import
    """分数算子注册器"""
    
    def __init__(self):
        self.calculators: List[FractionCalculator] = []
        self._register_default_calculators()
    
    def _register_default_calculators(self):
        """注册默认的分数算子"""
        from .calculators.ratio_equation import RatioEquationCalculator
        from .calculators.integer_fraction_compare import IntegerFractionCompareCalculator
        from .calculators.ratio_to_fraction import RatioToFractionCalculator
        from .calculators.reduce_fraction import ReduceFractionCalculator
        from .calculators.reciprocal import ReciprocalCalculator
        from .calculators.reciprocal_equation import ReciprocalEquationCalculator
        from .calculators.decimal_to_fraction import DecimalToFractionCalculator
        from .calculators.same_denominator_add import SameDenominatorAddCalculator
        from .calculators.same_denominator_subtract import SameDenominatorSubtractCalculator
        from .calculators.different_denominator_add import DifferentDenominatorAddCalculator
        from .calculators.different_denominator_subtract import DifferentDenominatorSubtractCalculator
        from .calculators.fraction_multiply import FractionMultiplyCalculator
        from .calculators.fraction_integer_multiply import FractionIntegerMultiplyCalculator
        from .calculators.fraction_divide import FractionDivideCalculator
        from .calculators.fraction_compare import FractionCompareCalculator
        from .calculators.same_numerator_compare import SameNumeratorCompareCalculator
        from .calculators.cross_multiply_compare import CrossMultiplyCompareCalculator
        from .calculators.expression_compare import ExpressionCompareCalculator
        from .calculators.fraction_convert import FractionConvertCalculator
        from .calculators.mixed_improper_convert import MixedImproperConvertCalculator
        from .calculators.fraction_to_decimal import FractionToDecimalCalculator
        from .calculators.ratio_to_value import RatioToValueCalculator
        
        # 按优先级注册算子（优先级高的先注册）
        calculators = [
            RatioToValueCalculator(),
            RatioEquationCalculator(),
            FractionToDecimalCalculator(),
            # 新增算子
            IntegerFractionCompareCalculator(),
            RatioToFractionCalculator(),
            # 特殊算子
            ReciprocalEquationCalculator(),    # 9
            ReciprocalCalculator(),            # 8
            DecimalToFractionCalculator(),     # 11
            # 比较算子
            SameNumeratorCompareCalculator(),  # 2 - 同分子比较优先级最高
            FractionCompareCalculator(),       # 3 - 通用比较（包含同分母）
            CrossMultiplyCompareCalculator(),  # 4 - 交叉相乘
            ExpressionCompareCalculator(),     # 5 - 运算后比较
            # 运算算子
            SameDenominatorAddCalculator(),    # 6
            SameDenominatorSubtractCalculator(), # 6
            DifferentDenominatorAddCalculator(), # 7
            DifferentDenominatorSubtractCalculator(), # 7
            FractionMultiplyCalculator(),      # 5
            FractionIntegerMultiplyCalculator(), # 5
            FractionDivideCalculator(),        # 5
            # 转换算子
            ReduceFractionCalculator(),        # 10
            FractionConvertCalculator(),       # 12
            MixedImproperConvertCalculator(),  # 4
        ]
        
        for calc in calculators:
            self.register(calc)
    
    def register(self, calculator: FractionCalculator):
        """注册算子"""
        self.calculators.append(calculator)
        # 按优先级排序（高优先级在前）
        self.calculators.sort(key=lambda x: x.priority, reverse=True)
    
    def find_matching_calculators(self, problem: FractionProblem) -> List[FractionCalculator]:
        """找到匹配的算子"""
        matching = []
        
        for calculator in self.calculators:
            match_result = calculator.is_match_pattern(problem)
            if match_result.get("matched", False):
                matching.append(calculator)
        
        return matching
    
    def get_best_calculator(self, problem: FractionProblem) -> Optional[FractionCalculator]:
        """获取最佳算子"""
        matching = self.find_matching_calculators(problem)
        
        if not matching:
            return None
        
        # 按优先级和匹配分数排序
        matching.sort(key=lambda x: (x.priority, x.is_match_pattern(problem).get("score", 0)), reverse=True)
        
        return matching[0]
    
    def get_all_calculators(self) -> List[FractionCalculator]:
        """获取所有注册的算子"""
        return self.calculators.copy()
    
    def get_calculator_by_name(self, name: str) -> Optional[FractionCalculator]:
        """根据名称获取算子"""
        for calc in self.calculators:
            if calc.name == name:
                return calc
        return None
