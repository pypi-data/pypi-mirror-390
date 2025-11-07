"""
乘以25实现
利用25 = 100/4的特点，转换为除以4再乘100
优化版本：根据整除性选择计算路径
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByTwentyFive(MathCalculator):
    """乘以25算法"""
    
    def __init__(self):
        super().__init__("乘25速算", "任意整数乘25，根据整除性优化计算路径", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：任意数乘以25"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否有一个数是25
            return a == 25 or b == 25
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘25速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是25，哪个是被乘数
        if a == 25:
            multiplied_num = b
        else:
            multiplied_num = a
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 25 使用乘25速算法",
            operation="识别模式",
            result="25 = 100 ÷ 4，选择最优计算路径"
        ))
        
        # 检查是否能被4整除
        if multiplied_num % 4 == 0:
            return self._construct_divisible_by_four_steps(steps, multiplied_num)
        else:
            return self._construct_not_divisible_by_four_steps(steps, multiplied_num)
    
    def _construct_divisible_by_four_steps(self, steps: List[CalculationStep], multiplied_num: int) -> List[CalculationStep]:
        """构建能被4整除的计算步骤：先除4再乘100"""
        steps.append(CalculationStep(
            description=f"判断：{multiplied_num} 能被4整除",
            operation="整除性判断",
            result="采用路径：先除4，再乘100"
        ))
        
        quotient = multiplied_num // 4
        steps.append(CalculationStep(
            description=f"第一步：{multiplied_num} ÷ 4 = {quotient}",
            operation="除以4",
            result=quotient
        ))
        
        final_result = quotient * 100
        steps.append(CalculationStep(
            description=f"第二步：{quotient} × 100 = {final_result}",
            operation="乘以100（添两个零）",
            result=final_result,
            formula="能被4整除：a × 25 = (a ÷ 4) × 100"
        ))
        
        return steps
    
    def _construct_not_divisible_by_four_steps(self, steps: List[CalculationStep], multiplied_num: int) -> List[CalculationStep]:
        """构建不能被4整除的计算步骤：先乘100再除4"""
        steps.append(CalculationStep(
            description=f"判断：{multiplied_num} 不能被4整除",
            operation="整除性判断",
            result="采用路径：先乘100，再除4"
        ))
        
        temp_result = multiplied_num * 100
        steps.append(CalculationStep(
            description=f"第一步：{multiplied_num} × 100 = {temp_result}",
            operation="乘以100（添两个零）",
            result=temp_result
        ))
        
        final_result = temp_result // 4
        remainder = temp_result % 4
        
        if remainder == 0:
            steps.append(CalculationStep(
                description=f"第二步：{temp_result} ÷ 4 = {final_result}",
                operation="除以4",
                result=final_result,
                formula="不能被4整除：a × 25 = (a × 100) ÷ 4"
            ))
        else:
            # 处理有余数的情况（理论上25乘以整数不会出现，但为了完整性）
            decimal_result = temp_result / 4
            steps.append(CalculationStep(
                description=f"第二步：{temp_result} ÷ 4 = {decimal_result}",
                operation="除以4",
                result=decimal_result,
                formula="不能被4整除：a × 25 = (a × 100) ÷ 4"
            ))
            final_result = decimal_result
        
        return steps