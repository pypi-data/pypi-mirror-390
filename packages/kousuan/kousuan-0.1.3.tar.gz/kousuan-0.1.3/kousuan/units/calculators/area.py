"""
面积单位换算算子
支持所有平方相关单位（中英文）
"""
from typing import List, Dict
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep

class AreaUnitCalculator(UnitCalculator):
    """面积单位换算算子"""
    def __init__(self):
        super().__init__("面积单位换算", "处理平方米、平方分米、平方厘米、平方毫米等单位换算", UnitType.AREA)
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        return {
            # 平方千米
            "km²": {"km²": 1, "平方千米": 1, "公顷": 100, "m²": 1000000, "平方米": 1000000},
            "平方千米": {"km²": 1, "平方千米": 1, "公顷": 100, "m²": 1000000, "平方米": 1000000},
            # 公顷
            "ha": {"km²": 0.01, "平方千米": 0.01, "公顷": 1, "m²": 10000, "平方米": 10000},
            "公顷": {"km²": 0.01, "平方千米": 0.01, "公顷": 1, "m²": 10000, "平方米": 10000},
            # 平方米
            "m²": {"km²": 0.000001, "平方千米": 0.000001, "ha": 0.0001, "公顷": 0.0001, "m²": 1, "平方米": 1, "dm²": 100, "平方分米": 100, "cm²": 10000, "平方厘米": 10000, "mm²": 1000000, "平方毫米": 1000000},
            "平方米": {"km²": 0.000001, "平方千米": 0.000001, "ha": 0.0001, "公顷": 0.0001, "m²": 1, "平方米": 1, "dm²": 100, "平方分米": 100, "cm²": 10000, "平方厘米": 10000, "mm²": 1000000, "平方毫米": 1000000},
            # 平方分米
            "dm²": {"km²": 0.00000001, "平方千米": 0.00000001, "ha": 0.00001, "公顷": 0.00001, "m²": 0.01, "平方米": 0.01, "dm²": 1, "平方分米": 1, "cm²": 100, "平方厘米": 100, "mm²": 10000, "平方毫米": 10000},
            "平方分米": {"km²": 0.00000001, "平方千米": 0.00000001, "ha": 0.00001, "公顷": 0.00001, "m²": 0.01, "平方米": 0.01, "dm²": 1, "平方分米": 1, "cm²": 100, "平方厘米": 100, "mm²": 10000, "平方毫米": 10000},
            # 平方厘米
            "cm²": {"km²": 0.0000000001, "平方千米": 0.0000000001, "ha": 0.000001, "公顷": 0.000001, "m²": 0.0001, "平方米": 0.0001, "dm²": 0.01, "平方分米": 0.01, "cm²": 1, "平方厘米": 1, "mm²": 100, "平方毫米": 100},
            "平方厘米": {"km²": 0.0000000001, "平方千米": 0.0000000001, "ha": 0.000001, "公顷": 0.000001, "m²": 0.0001, "平方米": 0.0001, "dm²": 0.01, "平方分米": 0.01, "cm²": 1, "平方厘米": 1, "mm²": 100, "平方毫米": 100},
            # 平方毫米
            "mm²": {"km²": 0.000000000001, "平方千米": 0.000000000001, "ha": 0.0000001, "公顷": 0.0000001, "m²": 0.000001, "平方米": 0.000001, "dm²": 0.0001, "平方分米": 0.0001, "cm²": 0.01, "平方厘米": 0.01, "mm²": 1, "平方毫米": 1},
            "平方毫米": {"km²": 0.000000000001, "平方千米": 0.000000000001, "ha": 0.0000001, "公顷": 0.0000001, "m²": 0.000001, "平方米": 0.000001, "dm²": 0.0001, "平方分米": 0.0001, "cm²": 0.01, "平方厘米": 0.01, "mm²": 1, "平方毫米": 1},
        }
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        return problem.unit_type == UnitType.AREA
    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
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
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)
            step = ConversionStep(
                description=f"换算{source_value.unit}到{problem.target_unit}",
                operation="面积单位换算",
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
                description=f"合并面积换算结果",
                operation="面积求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(total_result, problem.target_unit),
                formula=f"总面积 = {formula}"
            )
            steps.append(step)
        return total_result, steps
    def _get_standard_formula(self, from_unit: str, to_unit: str) -> str:
        unit_hierarchy = {
            "km²": 6, "平方千米": 6,
            "ha": 5, "公顷": 5,
            "m²": 4, "平方米": 4,
            "dm²": 3, "平方分米": 3,
            "cm²": 2, "平方厘米": 2,
            "mm²": 1, "平方毫米": 1
        }
        from_level = unit_hierarchy.get(from_unit, 0)
        to_level = unit_hierarchy.get(to_unit, 0)
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
