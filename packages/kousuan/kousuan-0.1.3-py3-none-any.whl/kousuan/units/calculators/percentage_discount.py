"""
百分比和折扣换算算子
处理数字/小数与百分比、折扣之间的换算
"""

from typing import List, Dict
from decimal import Decimal, getcontext
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep

# 设置高精度计算
getcontext().prec = 28

cn_chars = '零一二三四五六七八九十'

class PercentageDiscountCalculator(UnitCalculator):
    """百分比和折扣换算算子"""
    
    def __init__(self):
        super().__init__("百分比折扣换算", "处理数字与百分比、折扣之间的换算", UnitType.PERCENTAGE)
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化百分比折扣换算规则"""
        return {
            # 小数到百分比：×100
            "": {"%": 100, "折": 10},
            "个": {"%": 100, "折": 10},
            
            # 百分比到小数：÷100
            "%": {"": 0.01, "个": 0.01, "折": 0.1},
            
            # 折扣到小数：÷10
            "折": {"": 0.1, "个": 0.1, "%": 10},
            "成": {"折": 1, "": 0.1, "个": 0.1, "%": 10}
        }
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为百分比折扣换算问题"""
        if problem.unit_type not in [UnitType.PERCENTAGE, UnitType.DISCOUNT]:
            return False
        
        # 检查是否涉及百分比或折扣单位
        source_units = [sv.unit for sv in problem.source_values]
        target_unit = problem.target_unit
        
        percentage_discount_units = ["", "个", "%", "折", "成"]
        return (any(unit in percentage_discount_units for unit in source_units) and 
                target_unit in percentage_discount_units)
    
    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解百分比折扣换算问题"""
        steps = []
        total_result = Decimal('0')
        
        for source_value in problem.source_values:
            # 处理空单位，统一为""
            from_unit = source_value.unit if source_value.unit else ""
            to_unit = problem.target_unit if problem.target_unit else ""
            
            # 获取换算系数
            conversion_factor = self._get_conversion_factor(from_unit, to_unit)
            
            if conversion_factor is None:
                raise ValueError(f"无法从{from_unit or '数字'}换算到{to_unit or '数字'}")
            
            # 使用Decimal进行高精度计算
            source_decimal = Decimal(str(source_value.value))
            factor_decimal = Decimal(str(conversion_factor))
            converted_decimal = source_decimal * factor_decimal
            
            converted_value = float(converted_decimal)
            total_result += converted_decimal
            
            # 添加换算原理说明
            principle_step = self._create_principle_explanation(from_unit, to_unit, conversion_factor)
            if principle_step:
                steps.append(principle_step)
            converted_value = self._round_result(converted_value)
            
            # 生成换算步骤
            from_display = f"{source_value.value}{from_unit}" if from_unit else str(source_value.value)
            to_display = f"{converted_value}{to_unit}" if to_unit else str(converted_value)
            
            step = ConversionStep(
                description=f"计算：{from_display} → {to_display}",
                operation="百分比折扣换算",
                from_value=source_value,
                result=UnitValue(converted_value, to_unit),
                formula=f"{source_value.value} × {conversion_factor} = {converted_value}"
            )
            steps.append(step)
        
        # 如果有多个源值，添加求和步骤
        if len(problem.source_values) > 1:
            step = ConversionStep(
                description=f"合并换算结果",
                operation="求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(float(total_result), problem.target_unit),
                formula=f"总计 = {' + '.join([str(v.value) for v in problem.source_values])}"
            )
            steps.append(step)
        
        # 四舍五入结果
        final_result = self._round_result(float(total_result))
        
        return final_result, steps
    
    def _get_conversion_factor(self, from_unit: str, to_unit: str) -> float:
        """获取换算系数"""
        conversion_rules = self._initialize_conversion_rules()
        
        # 处理空单位
        from_unit = from_unit if from_unit else ""
        to_unit = to_unit if to_unit else ""
        
        if from_unit in conversion_rules and to_unit in conversion_rules[from_unit]:
            return conversion_rules[from_unit][to_unit]
        
        return None
    
    def _create_principle_explanation(self, from_unit: str, to_unit: str, factor: float) -> ConversionStep:
        """创建换算原理说明步骤"""
        explanations = {
            ("", "%"): "小数转百分比：乘以100 (移动小数点2位)",
            ("个", "%"): "整数转百分比：乘以100",
            ("", "折"): "小数转折扣：乘以10 (移动小数点1位)",
            ("个", "折"): "整数转折扣：乘以10",
            ("%", ""): "百分比转小数：除以100 (移动小数点2位)",
            ("%", "个"): "百分比转整数：除以100",
            ("折", ""): "折扣转小数：除以10 (移动小数点1位)",
            ("折", "个"): "折扣转整数：除以10",
            ("%", "折"): "百分比转折扣：除以10",
            ("折", "%"): "折扣转百分比：乘以10"
        }
        
        key = (from_unit, to_unit)
        if key in explanations:
            return ConversionStep(
                description=explanations[key],
                operation="换算原理说明",
                from_value=UnitValue(1, from_unit),
                result=UnitValue(factor, to_unit),
                formula=f"换算系数：{factor}"
            )
        
        return None
    
    def _round_result(self, value: float) -> float:
        """四舍五入结果，避免浮点数精度问题"""
        # 对于百分比和折扣，保留4位小数精度
        return round(value, 4)


class PercentageCalculator(PercentageDiscountCalculator):
    """百分比换算算子"""
    
    def __init__(self):
        super().__init__()
        self.name = "百分比换算"
        self.description = "处理数字与百分比之间的换算"
        self.unit_type = UnitType.PERCENTAGE
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """匹配百分比换算问题"""
        if problem.unit_type != UnitType.PERCENTAGE:
            return False
        
        source_units = [sv.unit for sv in problem.source_values]
        target_unit = problem.target_unit
        
        # 涉及百分比的换算
        return ("%" in source_units or target_unit == "%") and target_unit != "折"


class DiscountCalculator(PercentageDiscountCalculator):
    """折扣换算算子"""
    
    def __init__(self):
        super().__init__()
        self.name = "折扣换算"
        self.description = "处理数字与折扣之间的换算"
        self.unit_type = UnitType.DISCOUNT
    
    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """匹配折扣换算问题"""
        if problem.unit_type != UnitType.DISCOUNT:
            return False
        
        source_units = [sv.unit for sv in problem.source_values]
        target_unit = problem.target_unit
        
        # 涉及折扣的换算
        return ("折" in source_units or target_unit == "折") and target_unit != "%"
