"""
混合运算算子注册器
"""

from typing import List, Dict, Any, Optional
from .base_types import MixedCalculator, MixedProblem


class MixedCalculatorRegistry:
    """混合运算算子注册器"""
    
    def __init__(self):
        self.calculators: List[MixedCalculator] = []
        self._register_default_calculators()
    
    def _register_default_calculators(self):
        """注册默认的混合运算算子"""
        from .calculators.parentheses_evaluator import ParenthesesEvaluator
        from .calculators.zero_one_optimizer import ZeroOneOptimizer
        from .calculators.mul_div_left_to_right import MulDivLeftToRightCalculator
        from .calculators.add_sub_left_to_right import AddSubLeftToRightCalculator
        from .calculators.standard_order_evaluator import StandardOrderEvaluator
        from .calculators.bracketed_mix_evaluator import BracketedMixEvaluator
        from .calculators.distribution_optimizer import DistributionOptimizer
        from .calculators.complement_rewriting import ComplementRewritingCalculator
        
        # 按优先级注册算子（优先级数字越小越优先）
        calculators = [
            ParenthesesEvaluator(),        # 1 - 括号优先
            BracketedMixEvaluator(),       # 2 - 含括号混合运算
            ZeroOneOptimizer(),            # 3 - 0/1优化（仅纯乘除）
            MulDivLeftToRightCalculator(), # 5 - 乘除链求值
            DistributionOptimizer(),       # 6 - 分配律优化
            ComplementRewritingCalculator(), # 7 - 凑整/补数重写
            AddSubLeftToRightCalculator(), # 8 - 加减链
            StandardOrderEvaluator(),      # 10 - 标准无括号混合求值（最后兜底）
        ]
        
        for calc in calculators:
            self.register(calc)
    
    def register(self, calculator: MixedCalculator):
        """注册算子"""
        self.calculators.append(calculator)
        # 按优先级排序（优先级数字小的在前）
        self.calculators.sort(key=lambda x: x.priority)
    
    def find_matching_calculators(self, problem: MixedProblem) -> List[MixedCalculator]:
        """找到匹配的算子"""
        matching = []
        
        for calculator in self.calculators:
            match_result = calculator.is_match_pattern(problem)
            if match_result.get("matched", False):
                matching.append(calculator)
        
        return matching
    
    def get_best_calculator(self, problem: MixedProblem) -> Optional[MixedCalculator]:
        """获取最佳算子"""
        matching = self.find_matching_calculators(problem)
        
        if not matching:
            return None
        
        # 按优先级和匹配分数排序
        matching.sort(key=lambda x: (x.priority, -x.is_match_pattern(problem).get("score", 0)))
        
        return matching[0]
    
    def get_all_calculators(self) -> List[MixedCalculator]:
        """获取所有注册的算子"""
        return self.calculators.copy()
    
    def get_calculator_by_name(self, name: str) -> Optional[MixedCalculator]:
        """根据名称获取算子"""
        for calc in self.calculators:
            if calc.name == name:
                return calc
        return None
