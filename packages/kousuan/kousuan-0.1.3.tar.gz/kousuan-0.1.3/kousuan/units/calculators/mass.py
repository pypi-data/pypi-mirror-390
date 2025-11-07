"""
质量单位换算算子
"""

from typing import List, Dict
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep


class MassUnitCalculator(UnitCalculator):
    """质量单位换算算子"""
    
    def __init__(self):
        super().__init__("质量单位换算", "处理吨、千克、克之间的换算", UnitType.MASS)
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化质量单位换算规则"""
        return {
            # 吨换算
            "t": {"t": 1, "kg": 1000, "g": 1000000},
            "吨": {"吨": 1, "千克": 1000, "公斤": 1000, "克": 1000000},
            
            # 千克换算
            "kg": {"t": 0.001, "kg": 1, "g": 1000},
            "千克": {"吨": 0.001, "千克": 1, "公斤": 1, "克": 1000},
            "公斤": {"吨": 0.001, "千克": 1, "公斤": 1, "克": 1000},
            
            # 克换算
            "g": {"t": 0.000001, "kg": 0.001, "g": 1},
            "克": {"吨": 0.000001, "千克": 0.001, "公斤": 0.001, "克": 1},
        }
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为质量单位换算问题"""
        return problem.unit_type == UnitType.MASS

    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解质量单位换算问题，支持 operator（+/-）单位运算"""
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
            operator = getattr(source_value, 'operator', '+')
            # 生成标准化的换算公式
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)
            step = ConversionStep(
                description=f"换算{source_value.unit}到{problem.target_unit}",
                operation="质量单位换算",
                from_value=source_value,
                result=UnitValue(converted_value, problem.target_unit),
                formula=formula
            )
            steps.append(step)
        if len(problem.source_values) > 1:
            formula_parts = []
            for v in problem.source_values:
                factor = self.get_conversion_factor(v.unit, problem.target_unit)
                if factor is not None:
                    formula_parts.append(str(v.value * factor) + getattr(v, 'operator', '+'))
                else:
                    formula_parts.append(str(v.value) + getattr(v, 'operator', '+'))
            formula = ' '.join(formula_parts).rstrip('+')
            step = ConversionStep(
                description=f"合并质量换算结果",
                operation="质量求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(total_result, problem.target_unit),
                formula=f"总质量 = {formula}"
            )
            steps.append(step)
        return total_result, steps
    
    def _get_standard_formula(self, from_unit: str, to_unit: str) -> str:
        """获取标准化的换算公式（大单位 = 小单位倍数）"""
        # 定义单位大小顺序（从大到小）
        unit_hierarchy = {
            "t": 3, "吨": 3,
            "kg": 2, "千克": 2, "公斤": 2,
            "g": 1, "克": 1
        }
        
        from_level = unit_hierarchy.get(from_unit, 0)
        to_level = unit_hierarchy.get(to_unit, 0)
        
        # 确定哪个是大单位，哪个是小单位
        if from_level > to_level:
            big_unit, small_unit = from_unit, to_unit
            factor = self.get_conversion_factor(from_unit, to_unit)
        else:
            big_unit, small_unit = to_unit, from_unit
            conv = self.get_conversion_factor(from_unit, to_unit)
            factor = 1 / conv if conv and conv != 0 else 1
        if factor and factor != 1:
            if factor == int(factor):
                return f"1{big_unit} = {int(factor)}{small_unit}"
            else:
                return f"1{big_unit} = {factor}{small_unit}"
        else:
            return f"1{from_unit} = 1{to_unit}"
