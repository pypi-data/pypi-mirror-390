"""
长度单位换算算子
"""

from typing import List, Dict
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep


class LengthUnitCalculator(UnitCalculator):
    """长度单位换算算子"""
    
    def __init__(self):
        super().__init__("长度单位换算", "处理千米、米、分米、厘米、毫米之间的换算", UnitType.LENGTH)
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化长度单位换算规则"""
        return {
            # 千米换算
            "km": {"km": 1, "m": 1000, "dm": 10000, "cm": 100000, "mm": 1000000},
            "千米": {"千米": 1, "米": 1000, "分米": 10000, "厘米": 100000, "毫米": 1000000},
            "公里": {"公里": 1, "米": 1000, "分米": 10000, "厘米": 100000, "毫米": 1000000},
            
            # 米换算
            "m": {"km": 0.001, "m": 1, "dm": 10, "cm": 100, "mm": 1000},
            "米": {"千米": 0.001, "米": 1, "分米": 10, "厘米": 100, "毫米": 1000},
            
            # 分米换算
            "dm": {"km": 0.0001, "m": 0.1, "dm": 1, "cm": 10, "mm": 100},
            "分米": {"千米": 0.0001, "米": 0.1, "分米": 1, "厘米": 10, "毫米": 100},
            
            # 厘米换算
            "cm": {"km": 0.00001, "m": 0.01, "dm": 0.1, "cm": 1, "mm": 10},
            "厘米": {"千米": 0.00001, "米": 0.01, "分米": 0.1, "厘米": 1, "毫米": 10},
            
            # 毫米换算
            "mm": {"km": 0.000001, "m": 0.001, "dm": 0.01, "cm": 0.1, "mm": 1},
            "毫米": {"千米": 0.000001, "米": 0.001, "分米": 0.01, "厘米": 0.1, "毫米": 1},
        }
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为长度单位换算问题"""
        return problem.unit_type == UnitType.LENGTH

    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解长度单位换算问题"""
        steps = []
        total_result = 0
        operator = "+"
        # 处理复合单位（如3m5dm）
        for source_value in problem.source_values:
            # 直接换算到目标单位
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
            
            # 生成标准化的换算公式
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)
            
            # 生成换算步骤
            step = ConversionStep(
                description=f"换算{source_value.unit}到{problem.target_unit}",
                operation="单位换算",
                from_value=source_value,
                result=UnitValue(converted_value, problem.target_unit),
                formula=formula
            )
            steps.append(step)
        
        # 如果有多个源单位，添加求和步骤
        if len(problem.source_values) > 1:
            formula = ' '.join([str(v.value * self.get_conversion_factor(v.unit, problem.target_unit)) + v.operator for v in problem.source_values]).rstrip('+')
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
        # 定义单位大小顺序（从大到小）
        unit_hierarchy = {
            "km": 5, "千米": 5, "公里": 5,
            "m": 4, "米": 4,
            "dm": 3, "分米": 3,
            "cm": 2, "厘米": 2,
            "mm": 1, "毫米": 1
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
