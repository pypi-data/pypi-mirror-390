"""
分段求和法加法实现
将数字按照数位或意义进行分段，分别计算各段的和，最后合并
适用于数位差异明显或有特殊结构的加法，如10+100
"""

from typing import List, Tuple
from ..base_types import MathCalculator, Formula, CalculationStep


class SegmentSumAddition(MathCalculator):
    """分段求和法加法算法"""
    
    def __init__(self):
        super().__init__("分段求和法", "按数位或意义分段计算，适用于结构清晰的加法", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：适用于数位结构差异明显或有特殊规律的加法"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, (int, float)) and isinstance(addend2, (int, float))):
                return False
            
            # 转换为整数
            addend1, addend2 = int(addend1), int(addend2)
            
            # 只处理正数
            if addend1 <= 0 or addend2 <= 0:
                return False
            
            # 适用条件：
            # 1. 其中一个数是整十、整百、整千数
            # 2. 两数位数差异较大（如10+100, 25+200）
            # 3. 两数都是特殊结构（如都是整十数的倍数）
            
            def is_round_number(n):
                """判断是否为整十、整百、整千等圆整数"""
                if n < 10:
                    return False
                return n % 10 == 0 or n % 100 == 0 or n % 1000 == 0
            
            def get_digit_count(n):
                """获取数位数"""
                return len(str(n))
            
            # 条件1：至少一个是圆整数
            if is_round_number(addend1) or is_round_number(addend2):
                return True
            
            # 条件2：位数差异大于1
            if abs(get_digit_count(addend1) - get_digit_count(addend2)) > 1:
                return True
            
            # 条件3：都是特殊结构（如25+75这样的互补数，或都是5的倍数等）
            if (addend1 % 5 == 0 and addend2 % 5 == 0) or (addend1 % 25 == 0 and addend2 % 25 == 0):
                return True
            
            return False
        except:
            return False
    
    def _analyze_segments(self, number: int) -> List[Tuple[str, int]]:
        """分析数字的分段结构，返回(段名称, 段值)的列表"""
        if number == 0:
            return [("零", 0)]
        
        segments = []
        
        # 按权重分段
        if number >= 1000:
            thousands = (number // 1000) * 1000
            segments.append(("千位段", thousands))
            number -= thousands
        
        if number >= 100:
            hundreds = (number // 100) * 100
            segments.append(("百位段", hundreds))
            number -= hundreds
        
        if number >= 10:
            tens = (number // 10) * 10
            segments.append(("十位段", tens))
            number -= tens
        
        if number > 0:
            segments.append(("个位段", number))
        
        return segments
    
    def _find_meaningful_segments(self, addend1: int, addend2: int) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
        """寻找有意义的分段方式"""
        # 基本的数位分段
        segments1 = self._analyze_segments(addend1)
        segments2 = self._analyze_segments(addend2)
        
        # 特殊优化：如果一个数是另一个数的整倍数关系
        if addend2 != 0 and addend1 % addend2 == 0:
            segments1 = [(f"{addend1//addend2}倍{addend2}", addend1)]
            segments2 = [("基数", addend2)]
        elif addend1 != 0 and addend2 % addend1 == 0:
            segments1 = [("基数", addend1)]
            segments2 = [(f"{addend2//addend1}倍{addend1}", addend2)]
        
        return segments1, segments2
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建分段求和法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用分段求和法",
            operation="识别分段求和法",
            result="按数位或意义进行分段计算"
        ))
        
        # 分析分段
        segments1, segments2 = self._find_meaningful_segments(addend1, addend2)
        
        # 显示分段识别
        segments1_str = "、".join([f"{name}({value})" for name, value in segments1])
        segments2_str = "、".join([f"{name}({value})" for name, value in segments2])
        
        steps.append(CalculationStep(
            description=f"识别分段结构",
            operation="分段识别",
            result=f"{addend1} 包含: {segments1_str}；{addend2} 包含: {segments2_str}"
        ))
        
        # 列出各段数值
        all_segments = []
        all_segments.extend([(name, value) for name, value in segments1])
        all_segments.extend([(name, value) for name, value in segments2])
        
        segment_list = []
        for name, value in all_segments:
            segment_list.append(f"{name}: {value}")
        
        steps.append(CalculationStep(
            description=f"列出各段数值",
            operation="段值列举",
            result="; ".join(segment_list)
        ))
        
        # 将各段数值相加
        segment_values = [value for _, value in all_segments]
        if len(segment_values) > 1:
            sum_expression = " + ".join([str(value) for value in segment_values])
            final_result = sum(segment_values)
            
            steps.append(CalculationStep(
                description=f"将各段数值相加：{sum_expression} = {final_result}",
                operation="分段求和",
                result=final_result
            ))
        else:
            final_result = segment_values[0] if segment_values else 0
        
        steps.append(CalculationStep(
            description=f"最终答案：{final_result}",
            operation="确认结果",
            result=final_result,
            formula="分段求和法：按结构分段后逐段相加"
        ))
        
        return steps