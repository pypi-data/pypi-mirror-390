"""
货币单位换算算子
"""

from typing import List, Dict
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep


class CurrencyUnitCalculator(UnitCalculator):
    """货币单位换算算子"""
    
    def __init__(self):
        super().__init__("货币单位换算", "处理元、角、分之间的换算", UnitType.CURRENCY)
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化货币单位换算规则"""
        return {
            # 元换算
            "元": {"元": 1, "角": 10, "分": 100, "¥": 1},
            "¥": {"¥": 1, "角": 10, "分": 100, "元": 1},
            
            # 角换算
            "角": {"元": 0.1, "¥": 0.1, "角": 1, "分": 10},
            "jiao": {"元": 0.1, "¥": 0.1, "角": 1, "分": 10},
            
            # 分换算
            "分": {"元": 0.01, "¥": 0.01, "角": 0.1, "分": 1},
            "fen": {"元": 0.01, "¥": 0.01, "角": 0.1, "分": 1},
        }
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为货币单位换算问题"""
        ## 如果是时间相关单位不能匹配，区分开“分”作为时间单位的情况
        if '时' in problem.original_text or '秒' in problem.original_text:
            return False
        return problem.unit_type == UnitType.CURRENCY

    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解货币单位换算问题"""
        steps = []
        total_result = 0
        operator = "+"
        for source_value in problem.source_values:
            conversion_factor = self.get_conversion_factor(source_value.unit, problem.target_unit)
            
            if conversion_factor is None:
                raise ValueError(f"无法从{source_value.unit}换算到{problem.target_unit}")
            
            converted_value = source_value.value * conversion_factor
            if operator == '-':
                total_result -= converted_value
            elif operator == '+':
                total_result += converted_value
            operator = source_value.operator
            
            # 生成标准化的换算公式
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)
            
            step = ConversionStep(
                description=f"换算{source_value.unit}到{problem.target_unit}",
                operation="货币单位换算",
                from_value=source_value,
                result=UnitValue(converted_value, problem.target_unit),
                formula=formula
            )
            steps.append(step)
        
        if len(problem.source_values) > 1:
            formula = ' '.join([str(v.value * self.get_conversion_factor(v.unit, problem.target_unit)) + v.operator for v in problem.source_values]).rstrip('+')
            step = ConversionStep(
                description=f"合并货币换算结果",
                operation="货币求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(total_result, problem.target_unit),
                formula=f"总金额 = {formula}"
            )
            steps.append(step)
        
        return total_result, steps
    
    def _get_standard_formula(self, from_unit: str, to_unit: str) -> str:
        """获取标准化的换算公式（大单位 = 小单位倍数）"""
        # 定义单位大小顺序（从大到小）
        unit_hierarchy = {
            "元": 3, "¥": 3,
            "角": 2, "jiao": 2,
            "分": 1, "fen": 1
        }
        
        from_level = unit_hierarchy.get(from_unit, 0)
        to_level = unit_hierarchy.get(to_unit, 0)
        
        # 确定哪个是大单位，哪个是小单位
        if from_level > to_level:
            # 从大单位换到小单位
            big_unit, small_unit = from_unit, to_unit
            factor = self.get_conversion_factor(from_unit, to_unit)
        else:
            # 从小单位换到大单位
            big_unit, small_unit = to_unit, from_unit
            factor = 1 / self.get_conversion_factor(from_unit, to_unit) if self.get_conversion_factor(from_unit, to_unit) else 1
        
        # 生成标准公式
        if factor and factor != 1:
            if factor == int(factor):
                return f"1{big_unit} = {int(factor)}{small_unit}"
            else:
                return f"1{big_unit} = {factor}{small_unit}"
        else:
            return f"1{from_unit} = 1{to_unit}"
