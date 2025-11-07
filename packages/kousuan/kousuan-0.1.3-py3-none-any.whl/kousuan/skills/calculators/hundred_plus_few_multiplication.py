"""
几百零几乘法实现
适用于几百零几乘以个位数和两位数
算法思路：拆分为百位和个位计算，最后合并结果
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class HundredPlusFewMultiplication(MathCalculator):
    """几百零几乘法算法"""
    
    def __init__(self):
        super().__init__("几百零几乘法", "几百零几乘以个位数或两位数，拆分计算后合并", priority=4)
    
    def _is_hundred_plus_few(self, num: int) -> tuple:
        """判断是否为几百零几，返回(是否匹配, 百位数, 个位数)"""
        if not isinstance(num, int) or num < 100 or num >= 1000:
            return False, 0, 0
        
        str_num = str(num)
        if len(str_num) != 3:
            return False, 0, 0
        
        # 检查十位是否为0
        if str_num[1] != '0':
            return False, 0, 0
        
        hundred_digit = int(str_num[0])
        unit_digit = int(str_num[2])
        
        return True, hundred_digit, unit_digit
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：几百零几乘以个位数或两位数"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查一个数是几百零几，另一个数是个位数或两位数
            is_hundred_a, _, _ = self._is_hundred_plus_few(a)
            is_hundred_b, _, _ = self._is_hundred_plus_few(b)
            
            if is_hundred_a and 1 <= b <= 99:
                return True
            elif is_hundred_b and 1 <= a <= 99:
                return True
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建几百零几乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是几百零几，哪个是乘数
        is_hundred_a, hundred_a, unit_a = self._is_hundred_plus_few(a)
        is_hundred_b, hundred_b, unit_b = self._is_hundred_plus_few(b)
        
        if is_hundred_a:
            hundred_num, hundred_digit, unit_digit = a, hundred_a, unit_a
            multiplier = b
        else:
            hundred_num, hundred_digit, unit_digit = b, hundred_b, unit_b
            multiplier = a
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{hundred_num} * {multiplier} 使用几百零几乘法",
            operation="识别几百零几乘法",
            result=f"{hundred_num} = {hundred_digit}00 + {unit_digit}"
        ))
        
        steps.append(CalculationStep(
            description=f"分解：{hundred_num} = {hundred_digit * 100} + {unit_digit}",
            operation="拆分被乘数",
            result=f"分别计算 {hundred_digit * 100} * {multiplier} 和 {unit_digit} * {multiplier}"
        ))
        
        # 判断乘数是个位数还是两位数
        if 1 <= multiplier <= 9:
            return self._construct_single_digit_steps(steps, hundred_digit, unit_digit, multiplier, hundred_num)
        else:
            return self._construct_two_digit_steps(steps, hundred_digit, unit_digit, multiplier, hundred_num)
    
    def _construct_single_digit_steps(self, steps: List[CalculationStep], hundred_digit: int, unit_digit: int, multiplier: int, hundred_num: int) -> List[CalculationStep]:
        """构建乘以个位数的步骤"""
        # 整百部分乘法
        hundred_part_result = hundred_digit * 100 * multiplier
        steps.append(CalculationStep(
            description=f"整百部分：{hundred_digit * 100} * {multiplier} = {hundred_part_result}",
            operation="整百乘法",
            result=hundred_part_result
        ))
        
        # 个位部分乘法
        unit_part_result = unit_digit * multiplier
        steps.append(CalculationStep(
            description=f"个位部分：{unit_digit} * {multiplier} = {unit_part_result}",
            operation="个位乘法",
            result=unit_part_result
        ))
        
        # 合并结果
        final_result = hundred_part_result + unit_part_result
        steps.append(CalculationStep(
            description=f"合并结果：{hundred_part_result} + {unit_part_result} = {final_result}",
            operation="合并得数",
            result=final_result,
            formula="几百零几 * 个位数 = 整百乘法 + 个位乘法"
        ))
        
        return steps
    
    def _construct_two_digit_steps(self, steps: List[CalculationStep], hundred_digit: int, unit_digit: int, multiplier: int, hundred_num: int) -> List[CalculationStep]:
        """构建乘以两位数的步骤"""
        # 分解两位数乘数
        ten_digit = multiplier // 10
        unit_multiplier = multiplier % 10
        
        steps.append(CalculationStep(
            description=f"分解乘数：{multiplier} = {ten_digit * 10} + {unit_multiplier}",
            operation="分解乘数",
            result=f"分别用 {ten_digit * 10} 和 {unit_multiplier} 去乘"
        ))
        
        # 乘以十位数（相当于乘以整十数）
        ten_part_result = hundred_num * (ten_digit * 10)
        steps.append(CalculationStep(
            description=f"乘十位：{hundred_num} * {ten_digit * 10} = {ten_part_result}",
            operation="乘整十数",
            result=ten_part_result
        ))
        
        # 乘以个位数
        unit_hundred_part = hundred_digit * 100 * unit_multiplier
        unit_unit_part = unit_digit * unit_multiplier
        unit_total = unit_hundred_part + unit_unit_part
        
        steps.append(CalculationStep(
            description=f"乘个位：{hundred_num} * {unit_multiplier} = ({hundred_digit * 100} + {unit_digit}) * {unit_multiplier}",
            operation="乘个位数",
            result=f"{unit_hundred_part} + {unit_unit_part} = {unit_total}"
        ))
        
        # 最终合并
        final_result = ten_part_result + unit_total
        steps.append(CalculationStep(
            description=f"最终合并：{ten_part_result} + {unit_total} = {final_result}",
            operation="合并所有结果",
            result=final_result,
            formula="几百零几 * 两位数 = 整百×十位 + 整百×个位 + 零几×个位"
        ))
        
        return steps
