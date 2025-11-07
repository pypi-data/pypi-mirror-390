"""
立方体积单位换算算子
"""

from typing import List, Dict
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep

class VolumeUnitCalculator(UnitCalculator):
    """立方体积单位换算算子"""
    def __init__(self):
        super().__init__("立方体积单位换算", "处理立方米、立方分米、立方厘米、升、毫升之间的换算", UnitType.VOLUME)

    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        # 初始化立方体积单位换算规则，支持所有常见英文/中文表达
        return {
        # 立方米
        "m³": {"m³": 1, "m³": 1, "dm³": 1000, "dm³": 1000, "cm³": 1000000, "cm³": 1000000, "L": 1000, "mL": 1000000,
            "立方米": 1, "立方分米": 1000, "立方厘米": 1000000, "升": 1000, "毫升": 1000000},
        "m³": {"m³": 1, "m³": 1, "dm³": 1000, "dm³": 1000, "cm³": 1000000, "cm³": 1000000, "L": 1000, "mL": 1000000,
            "立方米": 1, "立方分米": 1000, "立方厘米": 1000000, "升": 1000, "毫升": 1000000},
        "立方米": {"m³": 1, "m³": 1, "dm³": 1000, "dm³": 1000, "cm³": 1000000, "cm³": 1000000, "L": 1000, "mL": 1000000,
              "立方米": 1, "立方分米": 1000, "立方厘米": 1000000, "升": 1000, "毫升": 1000000},
        # 立方分米
        "dm³": {"m³": 0.001, "m³": 0.001, "dm³": 1, "dm³": 1, "cm³": 1000, "cm³": 1000, "L": 1, "mL": 1000,
             "立方米": 0.001, "立方分米": 1, "立方厘米": 1000, "升": 1, "毫升": 1000},
        "dm³": {"m³": 0.001, "m³": 0.001, "dm³": 1, "dm³": 1, "cm³": 1000, "cm³": 1000, "L": 1, "mL": 1000,
             "立方米": 0.001, "立方分米": 1, "立方厘米": 1000, "升": 1, "毫升": 1000},
        "立方分米": {"m³": 0.001, "m³": 0.001, "dm³": 1, "dm³": 1, "cm³": 1000, "cm³": 1000, "L": 1, "mL": 1000,
            "立方米": 0.001, "立方分米": 1, "立方厘米": 1000, "升": 1, "毫升": 1000},
        # 立方厘米
        "cm³": {"m³": 0.000001, "m³": 0.000001, "dm³": 0.001, "dm³": 0.001, "cm³": 1, "cm³": 1, "L": 0.001, "mL": 1,
             "立方米": 0.000001, "立方分米": 0.001, "立方厘米": 1, "升": 0.001, "毫升": 1},
        "cm³": {"m³": 0.000001, "m³": 0.000001, "dm³": 0.001, "dm³": 0.001, "cm³": 1, "cm³": 1, "L": 0.001, "mL": 1,
             "立方米": 0.000001, "立方分米": 0.001, "立方厘米": 1, "升": 0.001, "毫升": 1},
        "立方厘米": {"m³": 0.000001, "m³": 0.000001, "dm³": 0.001, "dm³": 0.001, "cm³": 1, "cm³": 1, "L": 0.001, "mL": 1,
            "立方米": 0.000001, "立方分米": 0.001, "立方厘米": 1, "升": 0.001, "毫升": 1},
        # 升
        "L": {"m³": 0.001, "m³": 0.001, "dm³": 1, "dm³": 1, "cm³": 1000, "cm³": 1000, "L": 1, "mL": 1000,
          "立方米": 0.001, "立方分米": 1, "立方厘米": 1000, "升": 1, "毫升": 1000},
        "升": {"m³": 0.001, "m³": 0.001, "dm³": 1, "dm³": 1, "cm³": 1000, "cm³": 1000, "L": 1, "mL": 1000,
           "立方米": 0.001, "立方分米": 1, "立方厘米": 1000, "升": 1, "毫升": 1000},
        # 毫升
        "mL": {"m³": 0.000001, "m³": 0.000001, "dm³": 0.001, "dm³": 0.001, "cm³": 1, "cm³": 1, "L": 0.001, "mL": 1,
            "立方米": 0.000001, "立方分米": 0.001, "立方厘米": 1, "升": 0.001, "毫升": 1},
        "毫升": {"m³": 0.000001, "m³": 0.000001, "dm³": 0.001, "dm³": 0.001, "cm³": 1, "cm³": 1, "L": 0.001, "mL": 1,
             "立方米": 0.000001, "立方分米": 0.001, "立方厘米": 1, "升": 0.001, "毫升": 1},
    }

    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为立方体积单位换算问题"""
        return problem.unit_type == UnitType.VOLUME

    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解立方体积单位换算问题"""
        steps = []
        total_result = 0
        operator = "+"
        for source_value in problem.source_values:
            conversion_factor = self.get_conversion_factor(source_value.unit, problem.target_unit)
            if conversion_factor is None:
                print(f"无法从{source_value.unit}换算到{problem.target_unit}")
                raise ValueError(f"无法从{source_value.unit}换算到{problem.target_unit}")
            converted_value = source_value.value * conversion_factor
            if operator == '-':
                total_result -= converted_value
            elif operator == '+':
                total_result += converted_value
            operator = source_value.operator
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)
            step = ConversionStep(
                description=f"换算{source_value.unit}到{problem.target_unit}",
                operation="单位换算",
                from_value=source_value,
                result=UnitValue(converted_value, problem.target_unit),
                formula=formula
            )
            steps.append(step)
        if len(problem.source_values) > 1:
            formula_parts = []
            for v in problem.source_values:
                factor = self.get_conversion_factor(v.unit, problem.target_unit)
                if factor is None:
                    raise ValueError(f"无法从{v.unit}换算到{problem.target_unit}")
                formula_parts.append(str(v.value * factor) + v.operator)
            formula = ' '.join(formula_parts).rstrip('+')
            step = ConversionStep(
                description=f"合并所有换算结果",
                operation="求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(total_result, problem.target_unit),
                formula=f"总和 = {formula}"
            )
            steps.append(step)
        return total_result, steps

    def _get_standard_formula(self, from_unit: str, to_unit: str) -> str:
        """获取标准化的换算公式（大单位 = 小单位倍数）"""
        unit_hierarchy = {
            "m³": 5, "立方米": 5,
            "dm³": 4, "立方分米": 4, "L": 4, "升": 4,
            "cm³": 3, "立方厘米": 3, "mL": 3, "毫升": 3
        }
        from_level = unit_hierarchy.get(from_unit, 0)
        to_level = unit_hierarchy.get(to_unit, 0)
        factor = self.get_conversion_factor(from_unit, to_unit)
        if factor is None or factor == 0:
            return f"1{from_unit} = 1{to_unit}"
        if from_level > to_level:
            big_unit, small_unit = from_unit, to_unit
        else:
            big_unit, small_unit = to_unit, from_unit
            factor = 1 / factor if factor else 1
        if factor and factor != 1:
            if factor == int(factor):
                return f"1{big_unit} = {int(factor)}{small_unit}"
            else:
                return f"1{big_unit} = {factor}{small_unit}"
        else:
            return f"1{from_unit} = 1{to_unit}"
