"""
分拆法乘法实现
将其中一个数拆分成整十、整百数和另一个数的和，再分别相乘
通用技巧，尤其当其中一个数接近整十、整百时效果明显
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SplitMethodMultiplication(MathCalculator):
    """分拆法乘法算法"""
    
    def __init__(self):
        super().__init__("分拆法乘法", "将一个数拆分成便于计算的数的和再分别相乘", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：其中一个数可以拆分为便于计算的形式"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 转换为整数
            a, b = int(a), int(b)
            
            # 只处理两位数及以上
            if a < 10 or b < 10:
                return False
            
            # 检查是否有合适的分拆方式
            return self._find_best_split(a, b) is not None
            
        except:
            return False
    
    def _find_best_split(self, a: int, b: int):
        """寻找最佳分拆方式，返回(被分拆数, 另一数, 分拆方案)或None"""
        candidates = []
        
        # 尝试分拆a
        splits_a = self._get_useful_splits(a)
        for split in splits_a:
            score = self._calculate_split_score(split, b)
            candidates.append((a, b, split, score))
        
        # 尝试分拆b
        splits_b = self._get_useful_splits(b)
        for split in splits_b:
            score = self._calculate_split_score(split, a)
            candidates.append((b, a, split, score))
        
        if not candidates:
            return None
        
        # 选择得分最高的分拆方案
        candidates_with_score = [c for c in candidates if c[3] > 0]
        if not candidates_with_score:
            return None
        
        best = max(candidates_with_score, key=lambda x: x[3])
        return best[0], best[1], best[2]
    
    def _get_useful_splits(self, num: int) -> List[tuple]:
        """获取有用的分拆方案，返回(主要部分, 次要部分)的列表"""
        splits = []
        
        # 按十位分拆 (如13 = 10 + 3)
        if num >= 20:
            tens = (num // 10) * 10
            ones = num % 10
            if ones != 0:
                splits.append((tens, ones))
        
        # 按百位分拆 (如123 = 100 + 23)
        if num >= 200:
            hundreds = (num // 100) * 100
            remainder = num % 100
            if remainder != 0:
                splits.append((hundreds, remainder))
        
        # 接近整十数的分拆 (如12 = 10 + 2, 18 = 20 - 2)
        if 11 <= num <= 99:
            lower_ten = (num // 10) * 10
            upper_ten = lower_ten + 10
            
            if num - lower_ten <= 5:  # 更接近较小的十
                splits.append((lower_ten, num - lower_ten))
            elif upper_ten - num <= 5:  # 更接近较大的十
                splits.append((upper_ten, -(upper_ten - num)))
        
        # 接近整百数的分拆
        if 101 <= num <= 999:
            lower_hundred = (num // 100) * 100
            upper_hundred = lower_hundred + 100
            
            if num - lower_hundred <= 10:
                splits.append((lower_hundred, num - lower_hundred))
            elif upper_hundred - num <= 10:
                splits.append((upper_hundred, -(upper_hundred - num)))
        
        return splits
    
    def _calculate_split_score(self, split: tuple, other_num: int) -> int:
        """计算分拆方案的得分，得分越高越值得使用"""
        main_part, minor_part = split
        score = 0
        
        # 主要部分是10、100、1000的倍数加分
        if main_part % 10 == 0:
            score += 3
        if main_part % 100 == 0:
            score += 2
        if main_part % 1000 == 0:
            score += 1
        
        # 次要部分越小越好
        abs_minor = abs(minor_part)
        if abs_minor <= 5:
            score += 2
        elif abs_minor <= 10:
            score += 1
        
        # 避免无意义的分拆
        if abs_minor == 0 or abs_minor >= main_part / 2:
            score = 0
        
        return score
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建分拆法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 转换为整数
        a, b = int(a), int(b)
        
        # 找到最佳分拆方案
        result = self._find_best_split(a, b)
        if result is None:
            # 这种情况不应该发生，因为is_match_pattern已经过滤了
            raise ValueError("No suitable split found")
        
        split_num, other_num, split_data = result
        main_part, minor_part = split_data
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{a} × {b} 使用分拆法",
            operation="识别分拆法",
            result=f"将{split_num}分拆为更易计算的形式"
        ))
        
        # 显示分拆
        if minor_part >= 0:
            steps.append(CalculationStep(
                description=f"分拆：{split_num} = {main_part} + {minor_part}",
                operation="数字分拆",
                result=f"{split_num} = {main_part} + {minor_part}"
            ))
        else:
            steps.append(CalculationStep(
                description=f"分拆：{split_num} = {main_part} - {abs(minor_part)}",
                operation="数字分拆",
                result=f"{split_num} = {main_part} + ({minor_part})"
            ))
        
        # 应用分配律
        if minor_part >= 0:
            steps.append(CalculationStep(
                description=f"应用分配律：{other_num} × ({main_part} + {minor_part}) = {other_num} × {main_part} + {other_num} × {minor_part}",
                operation="分配律展开",
                result="分别计算两部分"
            ))
        else:
            steps.append(CalculationStep(
                description=f"应用分配律：{other_num} × ({main_part} + ({minor_part})) = {other_num} × {main_part} + {other_num} × ({minor_part})",
                operation="分配律展开",
                result="分别计算两部分"
            ))
        
        # 计算第一部分
        part1_result = other_num * main_part
        steps.append(CalculationStep(
            description=f"{other_num} × {main_part} = {part1_result}",
            operation="计算第一部分",
            result=part1_result
        ))
        
        # 计算第二部分
        part2_result = other_num * minor_part
        steps.append(CalculationStep(
            description=f"{other_num} × {minor_part} = {part2_result}",
            operation="计算第二部分", 
            result=part2_result
        ))
        
        # 合并结果
        final_result = part1_result + part2_result
        steps.append(CalculationStep(
            description=f"{part1_result} + ({part2_result}) = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="分拆法：a × (b + c) = a × b + a × c"
        ))
        
        return steps