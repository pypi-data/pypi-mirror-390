"""
两位数的平方实现
利用完全平方公式(a+b)²=a²+2ab+b²计算两位数平方
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class TwoDigitSquare(MathCalculator):
    """两位数的平方"""
    
    def __init__(self):
        super().__init__("两位数平方", "利用完全平方公式计算两位数平方", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两位数的平方"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 两个数必须相等且为两位数
            return (a == b and 10 <= abs(a) <= 99)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建两位数平方步骤"""
        numbers = formula.get_numbers()
        num = int(numbers[0].get_numeric_value())
        
        # 分解为十位和个位
        tens = num // 10
        ones = num % 10
        
        steps = []
        
        # 检查是否为个位数是5的特殊情况
        if ones == 5:
            return self._construct_ends_with_five_steps(num, tens)
        else:
            return self._construct_general_steps(num, tens, ones)
    
    def _construct_ends_with_five_steps(self, num: int, tens: int) -> List[CalculationStep]:
        """构建个位数是5的平方步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{num}² 使用个位是5的特殊公式",
            operation="识别特殊模式",
            result="个位是5的数平方：前面十位×(十位+1)，后面写25"
        ))
        
        steps.append(CalculationStep(
            description=f"提取十位数：{tens}",
            operation="提取十位",
            result=f"十位数 a = {tens}"
        ))
        
        # 计算十位×(十位+1)
        front_part = tens * (tens + 1)
        
        steps.append(CalculationStep(
            description=f"计算前半部分：{tens} × ({tens}+1) = {tens} × {tens + 1} = {front_part}",
            operation="计算前半部分",
            result=front_part
        ))
        
        steps.append(CalculationStep(
            description="后半部分固定为25",
            operation="确定后半部分",
            result=25
        ))
        
        # 最终结果
        final_result = front_part * 100 + 25
        
        steps.append(CalculationStep(
            description=f"组合结果：{front_part}|25 = {final_result}",
            operation="组合前后部分",
            result=final_result,
            formula="(10a+5)² = a×(a+1)×100 + 25"
        ))
        
        return steps
    
    def _construct_general_steps(self, num: int, tens: int, ones: int) -> List[CalculationStep]:
        """构建普通两位数平方步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{num}² 使用两位数平方公式",
            operation="识别模式",
            result="使用(a+b)²=a²+2ab+b²公式"
        ))
        
        steps.append(CalculationStep(
            description=f"分解：{num} = {tens * 10} + {ones}",
            operation="数字分解",
            result=f"十位：{tens}，个位：{ones}"
        ))
        
        # 计算各部分
        tens_square = (tens * 10) ** 2
        cross_product = 2 * (tens * 10) * ones
        ones_square = ones ** 2
        
        steps.append(CalculationStep(
            description=f"首平方：({tens * 10})² = {tens_square}",
            operation="计算首平方",
            result=tens_square
        ))
        
        steps.append(CalculationStep(
            description=f"首尾两倍：2 × {tens * 10} × {ones} = {cross_product}",
            operation="计算首尾两倍",
            result=cross_product
        ))
        
        steps.append(CalculationStep(
            description=f"尾平方：{ones}² = {ones_square}",
            operation="计算尾平方", 
            result=ones_square
        ))
        
        # 最终结果
        final_result = tens_square + cross_product + ones_square
        
        steps.append(CalculationStep(
            description=f"组合结果：{tens_square} + {cross_product} + {ones_square} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="(a+b)² = a² + 2ab + b²"
        ))
        
        return steps