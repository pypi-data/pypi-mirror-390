"""
分拆法加法实现
将复杂的加法拆分成多个简单的加法步骤
适用于较大数字或复杂结构的加法，如137+268可拆分为100+200+30+60+7+8
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SplitAddition(MathCalculator):
    """分拆法加法算法"""
    
    def __init__(self):
        super().__init__("分拆法", "将复杂加法拆分成多个简单步骤", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：适用于三位数及以上或特殊结构的加法"""
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
            
            # 适用于三位数及以上，或者两位数中有特殊拆分价值的
            if addend1 >= 100 or addend2 >= 100:
                return True
            
            # 两位数中，如果拆分后能产生更简单的计算，也适用
            # 例如：25+37可以拆分为20+30+5+7
            if addend1 >= 20 and addend2 >= 20:
                ones1, ones2 = addend1 % 10, addend2 % 10
                tens1, tens2 = addend1 // 10, addend2 // 10
                # 如果拆分后能产生整十数相加，则适用
                return (ones1 + ones2) != 0 and (ones1 + ones2) != 10
            
            return False
        except:
            return False
    
    def _split_number(self, number: int) -> List[tuple]:
        """将数字按位拆分，返回(位名称, 数值)的列表"""
        if number == 0:
            return [("个位", 0)]
        
        parts = []
        position_names = ["个位", "十位", "百位", "千位", "万位"]
        position = 0
        temp = number
        
        while temp > 0 and position < len(position_names):
            digit = temp % 10
            if digit > 0:
                place_value = digit * (10 ** position)
                parts.append((position_names[position], place_value))
            temp //= 10
            position += 1
        
        # 返回从高位到低位的顺序
        return list(reversed(parts))
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建分拆法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用分拆法",
            operation="识别分拆法",
            result="将数字按位分拆，逐步相加"
        ))
        
        # 分拆两个数字
        parts1 = self._split_number(addend1)
        parts2 = self._split_number(addend2)
        
        parts1_str = " + ".join([str(val) for _, val in parts1])
        parts2_str = " + ".join([str(val) for _, val in parts2])
        
        steps.append(CalculationStep(
            description=f"分拆数字",
            operation="数字分拆",
            result=f"{addend1} = {parts1_str}；{addend2} = {parts2_str}"
        ))
        
        # 重新组织算式
        all_parts = []
        all_parts.extend([val for _, val in parts1])
        all_parts.extend([val for _, val in parts2])
        
        reorganized = " + ".join([str(val) for val in all_parts])
        steps.append(CalculationStep(
            description=f"重新组织算式",
            operation="算式重组",
            result=f"原式 = {reorganized}"
        ))
        
        # 按位归类相加
        position_sums = {}
        for pos_name, val in parts1:
            if pos_name not in position_sums:
                position_sums[pos_name] = 0
            position_sums[pos_name] += val
        
        for pos_name, val in parts2:
            if pos_name not in position_sums:
                position_sums[pos_name] = 0
            position_sums[pos_name] += val
        
        # 按位次顺序计算
        position_order = ["万位", "千位", "百位", "十位", "个位"]
        partial_results = []
        
        for pos_name in position_order:
            if pos_name in position_sums:
                sum_val = position_sums[pos_name]
                partial_results.append(sum_val)
                
                # 找出该位的组成部分
                parts_in_position = []
                for pos, val in parts1:
                    if pos == pos_name:
                        parts_in_position.append(val)
                for pos, val in parts2:
                    if pos == pos_name:
                        parts_in_position.append(val)
                
                if len(parts_in_position) > 1:
                    parts_str = " + ".join([str(p) for p in parts_in_position])
                    steps.append(CalculationStep(
                        description=f"{pos_name}相加：{parts_str} = {sum_val}",
                        operation=f"{pos_name}计算",
                        result=sum_val
                    ))
                else:
                    steps.append(CalculationStep(
                        description=f"{pos_name}：{sum_val}（仅一个数有此位）",
                        operation=f"{pos_name}计算",
                        result=sum_val
                    ))
        
        # 合并所有位的结果
        final_result = sum(partial_results)
        if len(partial_results) > 1:
            partial_str = " + ".join([str(x) for x in partial_results])
            steps.append(CalculationStep(
                description=f"合并各位结果：{partial_str} = {final_result}",
                operation="合并结果",
                result=final_result,
                formula="分拆法：按位分拆后归类相加"
            ))
        else:
            steps.append(CalculationStep(
                description=f"最终结果：{final_result}",
                operation="确认结果",
                result=final_result,
                formula="分拆法：按位分拆后归类相加"
            ))
        
        return steps