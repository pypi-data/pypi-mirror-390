"""
数字单位换算算子
"""

from typing import List, Dict
from decimal import Decimal, getcontext
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep

# 设置高精度计算
getcontext().prec = 28

class NumberUnitCalculator(UnitCalculator):
    """数字单位换算算子"""
    
    def __init__(self):
        super().__init__("数字单位换算", "处理亿、千万、百万、十万、万、千、百之间的换算", UnitType.NUMBER)
        # 数字单位对应的零的个数
        self.unit_zeros = {
            "亿": 8,    # 1亿 = 100000000 (8个0)
            "千万": 7,  # 1千万 = 10000000 (7个0)
            "百万": 6,  # 1百万 = 1000000 (6个0)
            "十万": 5,  # 1十万 = 100000 (5个0)
            "万": 4,    # 1万 = 10000 (4个0)
            "千": 3,    # 1千 = 1000 (3个0)
            "百": 2,    # 1百 = 100 (2个0)
        }
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化数字单位换算规则"""
        return {
            # 亿换算
            "亿": {"亿": 1, "千万": 10, "百万": 100, "十万": 1000, "万": 10000, "千": 100000, "百": 1000000},
            
            # 千万换算
            "千万": {"亿": 0.1, "千万": 1, "百万": 10, "十万": 100, "万": 1000, "千": 10000, "百": 100000},
            
            # 百万换算
            "百万": {"亿": 0.01, "千万": 0.1, "百万": 1, "十万": 10, "万": 100, "千": 1000, "百": 10000},
            
            # 十万换算
            "十万": {"亿": 0.001, "千万": 0.01, "百万": 0.1, "十万": 1, "万": 10, "千": 100, "百": 1000},
            
            # 万换算
            "万": {"亿": 0.0001, "千万": 0.001, "百万": 0.01, "十万": 0.1, "万": 1, "千": 10, "百": 100},
            
            # 千换算
            "千": {"亿": 0.00001, "千万": 0.0001, "百万": 0.001, "十万": 0.01, "万": 0.1, "千": 1, "百": 10},
            
            # 百换算
            "百": {"亿": 0.000001, "千万": 0.00001, "百万": 0.0001, "十万": 0.001, "万": 0.01, "千": 0.1, "百": 1},
        }
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为数字单位换算问题"""
        return problem.unit_type == UnitType.NUMBER
    
    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解数字单位换算问题，支持@0000/@00000000等格式"""
        steps = []
        total_result = Decimal('0')

        # 自动识别@0000/@00000000等格式为标准单位
        target_unit = problem.target_unit
        if target_unit and target_unit.startswith('0') and set(target_unit) == {'0'}:
            zero_count = len(target_unit)
            # 反查标准单位
            unit_map = {v: k for k, v in self.unit_zeros.items()}
            if zero_count in unit_map:
                target_unit = unit_map[zero_count]
        elif target_unit and target_unit.startswith('@') and set(target_unit[1:]) == {'0'}:
            zero_count = len(target_unit) - 1
            unit_map = {v: k for k, v in self.unit_zeros.items()}
            if zero_count in unit_map:
                target_unit = unit_map[zero_count]
        # 替换为标准单位
        problem.target_unit = target_unit

        # 检查是否为单一数字到单位的换算
        if self._is_single_number_to_unit(problem):
            return self._solve_single_number_to_unit(problem)

        for source_value in problem.source_values:
            conversion_factor = self.get_conversion_factor(source_value.unit, problem.target_unit)

            if conversion_factor is None:
                raise ValueError(f"无法从{source_value.unit}换算到{problem.target_unit}")

            # 使用Decimal进行高精度计算
            source_decimal = Decimal(str(source_value.value))
            factor_decimal = Decimal(str(conversion_factor))
            converted_decimal = source_decimal * factor_decimal

            converted_value = float(converted_decimal)
            total_result += converted_decimal

            # 添加零的计数说明步骤
            zero_explanation_step = self._create_zero_explanation_step(source_value.unit, problem.target_unit)
            if zero_explanation_step:
                steps.append(zero_explanation_step)

            # 生成标准化的换算公式
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)

            # 生成换算步骤，显示具体的计算过程
            step = ConversionStep(
                description=f"换算{source_value.unit}到{problem.target_unit}：{source_value.value} × {conversion_factor}",
                operation="数字单位换算",
                from_value=source_value,
                result=UnitValue(converted_value, problem.target_unit),
                formula=formula
            )
            steps.append(step)

        # 如果有多个源单位，添加求和步骤
        if len(problem.source_values) > 1:
            step = ConversionStep(
                description=f"合并数字单位换算结果",
                operation="数字求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(float(total_result), problem.target_unit),
                formula=f"总数 = {' + '.join([f'{v.value}{v.unit}' for v in problem.source_values])}"
            )
            steps.append(step)

        # 四舍五入结果以避免浮点数精度问题
        final_result = self._round_result(float(total_result))

        return final_result, steps
    
    def _is_single_number_to_unit(self, problem: UnitProblem) -> bool:
        """判断是否为单纯数字到单位的换算 (如 46600000=@万)"""
        if len(problem.source_values) != 1:
            return False
        
        source_value = problem.source_values[0]
        # 源单位为空或"个"，目标单位为数字单位
        return (not source_value.unit or source_value.unit in ["", "个"]) and problem.target_unit in self.unit_zeros
    
    def _solve_single_number_to_unit(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """解决单纯数字到单位的换算"""
        steps = []
        source_value = problem.source_values[0]
        target_unit = problem.target_unit
        
        # 获取目标单位对应的基数
        unit_base = 10 ** self.unit_zeros[target_unit]
        zero_count = self.unit_zeros[target_unit]
        
        # 添加零的计数说明
        steps.append(ConversionStep(
            description=f"1{target_unit} = 1后面跟{zero_count}个0 = {unit_base}",
            operation="单位含义说明",
            from_value=UnitValue(1, target_unit),
            result=UnitValue(unit_base, ""),
            formula=f"1{target_unit} = 10^{zero_count} = {unit_base}"
        ))
        
        # 计算换算结果
        result = self._round_result(source_value.value / unit_base)
        
        # 添加换算步骤
        steps.append(ConversionStep(
            description=f"计算：{source_value.value} ÷ {unit_base} = {result}",
            operation="数字单位换算",
            from_value=source_value,
            result=UnitValue(result, target_unit),
            formula=f"{source_value.value} ÷ {unit_base} = {result}{target_unit}"
        ))
        
        # 如果结果是整数，转为整数显示
        if result == int(result):
            result = int(result)
        
        return result, steps
    
    def _create_zero_explanation_step(self, from_unit: str, to_unit: str) -> ConversionStep:
        """创建零的计数说明步骤"""
        if from_unit in self.unit_zeros and to_unit in self.unit_zeros:
            from_zeros = self.unit_zeros[from_unit]
            to_zeros = self.unit_zeros[to_unit]
            from_base = 10 ** from_zeros
            to_base = 10 ** to_zeros
            
            return ConversionStep(
                description=f"单位说明：1{from_unit}={from_base}({from_zeros}个0)，1{to_unit}={to_base}({to_zeros}个0)",
                operation="单位零的计数说明",
                from_value=UnitValue(1, from_unit),
                result=UnitValue(1, to_unit),
                formula=f"换算比例 = {from_base} ÷ {to_base} = {from_base/to_base}"
            )
        elif from_unit in self.unit_zeros:
            zeros = self.unit_zeros[from_unit]
            base = 10 ** zeros
            return ConversionStep(
                description=f"单位说明：1{from_unit} = {base} (1后面{zeros}个0)",
                operation="单位零的计数说明",
                from_value=UnitValue(1, from_unit),
                result=UnitValue(base, ""),
                formula=f"1{from_unit} = 10^{zeros} = {base}"
            )
        elif to_unit in self.unit_zeros:
            zeros = self.unit_zeros[to_unit]
            base = 10 ** zeros
            return ConversionStep(
                description=f"单位说明：1{to_unit} = {base} (1后面{zeros}个0)",
                operation="单位零的计数说明",
                from_value=UnitValue(base, ""),
                result=UnitValue(1, to_unit),
                formula=f"1{to_unit} = 10^{zeros} = {base}"
            )
        
        return None
    
    def _get_standard_formula(self, from_unit: str, to_unit: str) -> str:
        """获取标准化的换算公式（大单位 = 小单位倍数）"""
        # 定义单位大小顺序（从大到小）
        unit_hierarchy = {
            "亿": 7,
            "千万": 6,
            "百万": 5,
            "十万": 4,
            "万": 3,
            "千": 2,
            "百": 1
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
