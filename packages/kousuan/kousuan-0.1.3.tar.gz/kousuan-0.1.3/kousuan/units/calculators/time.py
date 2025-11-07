"""
时间单位换算算子
"""

from typing import List, Dict
from decimal import Decimal, getcontext
from ..base_types import UnitCalculator, UnitProblem, UnitType, UnitValue, ConversionStep
import datetime

# 设置高精度计算
getcontext().prec = 28

class TimeUnitCalculator(UnitCalculator):
    """时间单位换算算子"""
    
    def __init__(self):
        super().__init__("时间单位换算", "处理年、月、日、时、分、秒之间的换算", UnitType.TIME)
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, float]]:
        """初始化时间单位换算规则"""
        return {
            # 年换算（使用平均值，特殊情况在solve方法中处理）
            "年": {"年": 1, "month": 12, "月": 12, "日": 365.25, "天": 365.25, "时": 365.25*24, "小时": 365.25*24, "h": 365.25*24, "分": 365.25*24*60, "秒": 365.25*24*3600},
            "year": {"年": 1, "year": 1, "month": 12, "月": 12, "日": 365.25, "天": 365.25, "时": 365.25*24, "小时": 365.25*24, "h": 365.25*24},
            
            # 月换算（使用平均值，特殊情况在solve方法中处理）
            "月": {"年": 1/12, "year": 1/12, "月": 1, "month": 1, "日": 30.44, "天": 30.44, "时": 30.44*24, "小时": 30.44*24, "h": 30.44*24, "分": 30.44*24*60, "秒": 30.44*24*3600},
            "month": {"年": 1/12, "year": 1/12, "月": 1, "month": 1, "日": 30.44, "天": 30.44, "时": 30.44*24, "小时": 30.44*24, "h": 30.44*24},
            
            # 秒换算
            "s": {"s": 1, "min": 1/60, "h": 1/3600, "分": 1/60, "时": 1/3600, "小时": 1/3600, "秒": 1, "日": 1/(24*3600), "天": 1/(24*3600)},
            "秒": {"秒": 1, "分": 1/60, "时": 1/3600, "小时": 1/3600, "s": 1, "min": 1/60, "h": 1/3600, "日": 1/(24*3600), "天": 1/(24*3600)},
            
            # 分钟换算
            "min": {"s": 60, "min": 1, "h": 1/60, "秒": 60, "分": 1, "时": 1/60, "小时": 1/60, "日": 1/(24*60), "天": 1/(24*60)},
            "分": {"秒": 60, "分": 1, "时": 1/60, "小时": 1/60, "s": 60, "min": 1, "h": 1/60, "日": 1/(24*60), "天": 1/(24*60)},
            "分钟": {"秒": 60, "分钟": 1, "小时": 1/60, "s": 60, "min": 1, "h": 1/60, "分": 1, "时": 1/60, "日": 1/(24*60), "天": 1/(24*60)},
            
            # 小时换算
            "h": {"s": 3600, "min": 60, "h": 1, "秒": 3600, "分": 60, "时": 1, "小时": 1, "日": 1/24, "天": 1/24},
            "时": {"秒": 3600, "分": 60, "时": 1, "日": 1/24, "天": 1/24, "s": 3600, "min": 60, "h": 1, "小时": 1},
            "小时": {"秒": 3600, "分钟": 60, "小时": 1, "日": 1/24, "天": 1/24, "s": 3600, "min": 60, "h": 1, "分": 60, "时": 1},
            
            # 日换算
            "日": {"小时": 24, "时": 24, "h": 24, "日": 1, "天": 1, "分": 24*60, "秒": 24*3600, "月": 1/30.44, "month": 1/30.44, "年": 1/365.25, "year": 1/365.25},
            "天": {"小时": 24, "时": 24, "h": 24, "日": 1, "天": 1, "分": 24*60, "秒": 24*3600, "月": 1/30.44, "month": 1/30.44, "年": 1/365.25, "year": 1/365.25},
            "day": {"小时": 24, "时": 24, "h": 24, "日": 1, "天": 1, "day": 1},
        }
    
    def _is_leap_year(self, year: int) -> bool:
        """判断是否为闰年"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def _get_days_in_month(self, year: int, month: int) -> int:
        """获取指定年月的天数"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            return 29 if self._is_leap_year(year) else 28
        else:
            raise ValueError(f"无效的月份：{month}")
    
    def _get_days_in_year(self, year: int) -> int:
        """获取指定年份的天数"""
        return 366 if self._is_leap_year(year) else 365
    
    def parse_year_month(self, problem) -> UnitProblem:
        new_source_values = []
        for v in problem.source_values:
            if v.unit == "年":
                new_source_values.append(UnitValue(v.value * 12, "月"))
            else:
                new_source_values.append(v)
        problem = UnitProblem(
            original_text=problem.original_text,
            unit_type=problem.unit_type,
            source_values=new_source_values,
            target_unit=problem.target_unit
        )
        return problem
    
    def _handle_year_month_conversion(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """处理涉及年、月的特殊换算"""
        steps = []
        
        # 检查是否是特定年月到天数的转换
        source_units = [v.unit for v in problem.source_values]
        target_unit = problem.target_unit
        
        if len(problem.source_values) == 2 and "年" in source_units and "月" in source_units and target_unit in ["天", "日"]:
            # xx年x月有多少天的情况
            year_value = None
            month_value = None
            
            for source_value in problem.source_values:
                if source_value.unit == "年":
                    year_value = int(source_value.value)
                elif source_value.unit == "月":
                    month_value = int(source_value.value)
            
            if not year_value or year_value < 1000:
                return -1, []
            
            if year_value and month_value:
                days = self._get_days_in_month(year_value, month_value)
                
                steps.append(ConversionStep(
                    description=f"查找{year_value}年{month_value}月的天数",
                    operation="年月天数查询",
                    from_value=UnitValue(f"{year_value}年{month_value}月", ""),
                    result=UnitValue(days, target_unit),
                    formula=f"{year_value}年{month_value}月 = {days}天"
                ))
                
                # 添加闰年说明
                if month_value == 2:
                    leap_status = "闰年" if self._is_leap_year(year_value) else "平年"
                    steps.append(ConversionStep(
                        description=f"{year_value}年是{leap_status}，2月有{days}天",
                        operation="闰年判断",
                        from_value=UnitValue(year_value, "年"),
                        result=UnitValue(days, "天"),
                        formula=f"{leap_status}2月 = {days}天"
                    ))
                
                return float(days), steps
        
        # 其他年月换算使用标准流程
        return None, []

    def is_match_pattern(self, problem: UnitProblem) -> bool:
        """判断是否为时间单位换算问题"""
        return problem.unit_type == UnitType.TIME
    
    def solve(self, problem: UnitProblem) -> tuple[float, List[ConversionStep]]:
        """求解时间单位换算问题，支持 operator（+/-）单位运算"""
        # 先尝试特殊的年月换算
        special_result, special_steps = self._handle_year_month_conversion(problem)
        if special_result and len(special_steps) > 0:
            return special_result, special_steps
        elif special_result == -1:
            problem = self.parse_year_month(problem)
        steps = []
        total_result = Decimal('0')
        operator = "+"
        for source_value in problem.source_values:
            conversion_factor = self.get_conversion_factor(source_value.unit, problem.target_unit)
            if conversion_factor is None:
                raise ValueError(f"无法从{source_value.unit}换算到{problem.target_unit}")
            source_decimal = Decimal(str(source_value.value))
            factor_decimal = Decimal(str(conversion_factor))
            converted_decimal = source_decimal * factor_decimal
            converted_value = float(converted_decimal)
            if operator == '-':
                total_result -= converted_decimal
            elif operator == '+':
                total_result += converted_decimal
            operator = getattr(source_value, 'operator', '+')
            formula = self._get_standard_formula(source_value.unit, problem.target_unit)
            description = f"换算{source_value.unit}到{problem.target_unit}"
            result = UnitValue(converted_value, problem.target_unit)
            operation = "时间单位换算"
            if source_value.unit == problem.target_unit:
                description = f"{result}"
                operation = f"记录“{source_value.unit}”单位数值"
            step = ConversionStep(
                description=description,
                operation=operation,
                from_value=source_value,
                result=result,
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
                description=f"合并时间换算结果",
                operation="时间求和",
                from_value=UnitValue(0, problem.target_unit),
                result=UnitValue(float(total_result), problem.target_unit),
                formula=f"总时间 = {formula}"
            )
            steps.append(step)
        final_result = self._round_result(float(total_result))
        return final_result, steps
    
    def _get_standard_formula(self, from_unit: str, to_unit: str) -> str:
        """获取标准化的换算公式（大单位 = 小单位倍数）"""
        # 定义单位大小顺序（从大到小）
        unit_hierarchy = {
            "年": 6, "year": 6,
            "月": 5, "month": 5,
            "天": 4, "日": 4, "day": 4,
            "时": 3, "小时": 3, "h": 3,
            "分": 2, "分钟": 2, "min": 2,
            "秒": 1, "s": 1
        }

        # 如果单位相同，直接返回
        if from_unit == to_unit:
            return ""
        
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
                # 对于不是整数的换算，保留合理的小数位数
                if factor < 1:
                    return f"1{small_unit} = {1/factor:.6g}{big_unit}"
                else:
                    return f"1{big_unit} = {factor:.6g}{small_unit}"
        else:
            return f"1{from_unit} = 1{to_unit}"
