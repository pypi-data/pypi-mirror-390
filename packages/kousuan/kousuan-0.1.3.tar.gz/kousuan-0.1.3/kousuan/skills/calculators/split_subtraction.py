"""
分拆法减法实现
将被减数或减数拆分成更易计算的部分，再进行运算
避免借位，简化计算过程
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SplitSubtraction(MathCalculator):
    """分拆法减法算法"""
    
    def __init__(self):
        super().__init__("分拆法减法", "将数字拆分成便于计算的部分进行减法", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：可以通过拆分简化的减法"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, (int, float)) and isinstance(subtrahend, (int, float))):
                return False
            
            # 转换为整数
            minuend, subtrahend = int(minuend), int(subtrahend)
            
            # 只处理正数且被减数大于减数
            if minuend <= subtrahend or minuend < 10 or subtrahend < 10:
                return False
            
            # 检查是否有合适的拆分方式
            return self._find_best_split(minuend, subtrahend) is not None
            
        except:
            return False
    
    def _find_best_split(self, minuend: int, subtrahend: int):
        """寻找最佳拆分方式"""
        candidates = []
        
        # 拆分减数（更常用）
        subtrahend_splits = self._get_useful_splits(subtrahend)
        for split in subtrahend_splits:
            score = self._calculate_split_score(split, minuend, 'subtrahend')
            if score > 0:
                candidates.append(('subtrahend', split, score))
        
        # 拆分被减数（较少使用）
        minuend_splits = self._get_useful_splits(minuend)
        for split in minuend_splits:
            score = self._calculate_split_score(split, subtrahend, 'minuend')
            if score > 0:
                candidates.append(('minuend', split, score))
        
        if not candidates:
            return None
        
        # 选择得分最高的分拆方案
        best = max(candidates, key=lambda x: x[2])
        return best[0], best[1]
    
    def _get_useful_splits(self, num: int) -> List[tuple]:
        """获取有用的分拆方案，返回(主要部分, 次要部分)的列表"""
        splits = []
        
        # 按十位分拆 (如38 = 30 + 8)
        if num >= 20:
            tens = (num // 10) * 10
            ones = num % 10
            if ones != 0:
                splits.append((tens, ones))
        
        # 按百位分拆 (如238 = 200 + 38)
        if num >= 200:
            hundreds = (num // 100) * 100
            remainder = num % 100
            if remainder != 0:
                splits.append((hundreds, remainder))
        
        # 接近整十数的分拆 (如29 = 30 - 1, 31 = 30 + 1)
        if 11 <= num <= 99:
            lower_ten = (num // 10) * 10
            upper_ten = lower_ten + 10
            
            # 优先选择更接近的整十数
            if abs(num - lower_ten) <= abs(num - upper_ten):
                if num != lower_ten:
                    splits.append((lower_ten, num - lower_ten))
            else:
                splits.append((upper_ten, num - upper_ten))
        
        # 接近整百数的分拆
        if 101 <= num <= 999:
            lower_hundred = (num // 100) * 100
            upper_hundred = lower_hundred + 100
            
            # 优先选择更接近的整百数
            if abs(num - lower_hundred) <= abs(num - upper_hundred):
                if num != lower_hundred:
                    splits.append((lower_hundred, num - lower_hundred))
            else:
                splits.append((upper_hundred, num - upper_hundred))
        
        return splits
    
    def _calculate_split_score(self, split: tuple, other_num: int, split_type: str) -> int:
        """计算分拆方案的得分"""
        main_part, minor_part = split
        score = 0
        
        # 主要部分是整十、整百的倍数加分
        if main_part % 10 == 0:
            score += 3
        if main_part % 100 == 0:
            score += 2
        
        # 次要部分越小越好
        abs_minor = abs(minor_part)
        if abs_minor <= 5:
            score += 2
        elif abs_minor <= 10:
            score += 1
        
        # 检查拆分后是否能避免借位
        if split_type == 'subtrahend':
            # 拆分减数，检查是否避免借位
            if other_num >= main_part:  # 主要部分能减
                score += 2
            if (other_num - main_part) >= minor_part:  # 余数部分也能减
                score += 2
        
        # 避免无意义的分拆
        if abs_minor == 0 or abs_minor >= main_part:
            score = 0
        
        return score
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建分拆法步骤"""
        numbers = formula.get_numbers()
        minuend, subtrahend = [int(elem.get_numeric_value()) for elem in numbers]
        
        # 找到最佳拆分方案
        result = self._find_best_split(minuend, subtrahend)
        if result is None:
            raise ValueError("No suitable split found")
        
        split_type, (main_part, minor_part) = result
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用分拆法",
            operation="识别分拆法",
            result=f"将{'减数' if split_type == 'subtrahend' else '被减数'}分拆为便于计算的形式"
        ))
        
        if split_type == 'subtrahend':
            # 拆分减数
            if minor_part >= 0:
                steps.append(CalculationStep(
                    description=f"分拆减数：{subtrahend} = {main_part} + {minor_part}",
                    operation="减数分拆",
                    result=f"{subtrahend} = {main_part} + {minor_part}"
                ))
                
                steps.append(CalculationStep(
                    description=f"应用减法性质：{minuend} - ({main_part} + {minor_part}) = ({minuend} - {main_part}) - {minor_part}",
                    operation="减法性质",
                    result="分两步进行减法"
                ))
            else:
                steps.append(CalculationStep(
                    description=f"分拆减数：{subtrahend} = {main_part} - {abs(minor_part)}",
                    operation="减数分拆",
                    result=f"{subtrahend} = {main_part} + ({minor_part})"
                ))
                
                steps.append(CalculationStep(
                    description=f"应用减法性质：{minuend} - ({main_part} + ({minor_part})) = ({minuend} - {main_part}) - ({minor_part})",
                    operation="减法性质",
                    result="分两步进行减法"
                ))
            
            # 第一步计算
            step1_result = minuend - main_part
            steps.append(CalculationStep(
                description=f"第一步：{minuend} - {main_part} = {step1_result}",
                operation="计算第一步",
                result=step1_result
            ))
            
            # 第二步计算
            final_result = step1_result - minor_part
            steps.append(CalculationStep(
                description=f"第二步：{step1_result} - {minor_part} = {final_result}",
                operation="计算第二步",
                result=final_result
            ))
            
        else:
            # 拆分被减数
            if minor_part >= 0:
                steps.append(CalculationStep(
                    description=f"分拆被减数：{minuend} = {main_part} + {minor_part}",
                    operation="被减数分拆", 
                    result=f"{minuend} = {main_part} + {minor_part}"
                ))
                
                steps.append(CalculationStep(
                    description=f"应用减法性质：({main_part} + {minor_part}) - {subtrahend} = ({main_part} - {subtrahend}) + {minor_part}",
                    operation="减法性质",
                    result="分两步进行减法"
                ))
            else:
                steps.append(CalculationStep(
                    description=f"分拆被减数：{minuend} = {main_part} - {abs(minor_part)}",
                    operation="被减数分拆",
                    result=f"{minuend} = {main_part} + ({minor_part})"
                ))
            
            # 计算过程
            step1_result = main_part - subtrahend
            steps.append(CalculationStep(
                description=f"第一步：{main_part} - {subtrahend} = {step1_result}",
                operation="计算第一步",
                result=step1_result
            ))
            
            final_result = step1_result + minor_part
            steps.append(CalculationStep(
                description=f"第二步：{step1_result} + {minor_part} = {final_result}",
                operation="计算第二步",
                result=final_result
            ))
        
        steps.append(CalculationStep(
            description=f"最终结果：{final_result}",
            operation="确认结果",
            result=final_result,
            formula="分拆法：将复杂减法拆分为简单减法的组合"
        ))
        
        return steps