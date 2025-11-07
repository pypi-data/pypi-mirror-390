"""
差额法(求差法)乘法实现
两个数与某个中间数等距时，积等于中间数的平方减去距离的平方
适用于两个乘数关于一个整数对称的情况
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class DifferenceMethodMultiplication(MathCalculator):
    """差额法(求差法)乘法算法"""
    
    def __init__(self):
        super().__init__("差额法", "两数关于中间数对称时，积=中间数平方-距离平方", priority=6)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个乘数关于某个整数对称"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 转换为整数便于计算
            a, b = int(a), int(b)
            
            # 只处理正数且大于等于10的情况
            if a < 10 or b < 10:
                return False
            
            # 确保a <= b
            if a > b:
                a, b = b, a
            
            # 检查是否存在中间数使得两数对称
            # 中间数应该是 (a + b) / 2
            middle = (a + b) / 2
            
            # 中间数必须是整数或半整数
            if not (middle == int(middle) or middle == int(middle) + 0.5):
                return False
            
            # 中间数必需整十、整百的数
            if not (middle % 10 == 0 or middle % 100 == 0):
                return False
            
            # 计算距离
            distance = abs(b - middle)

            # 距离必需小于20
            if distance >= 20:
                return False
            # 距离应该相等且为正整数或半整数
            if abs(a - middle) != distance:
                return False
            
            # 距离不能太小（至少为1）且不能太大（保证有优化价值）
            return 1 <= distance <= 10
            
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建差额法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 转换为整数
        a, b = int(a), int(b)
        
        # 确保a <= b便于描述
        if a > b:
            a, b = b, a
        
        # 计算中间数和距离
        middle = (a + b) / 2
        distance = b - middle
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{a} × {b} 使用差额法",
            operation="识别差额法",
            result=f"两数关于中间数{middle}对称"
        ))
        
        steps.append(CalculationStep(
            description=f"计算中间数：({a} + {b}) ÷ 2 = {middle}",
            operation="计算中间数",
            result=middle
        ))
        
        steps.append(CalculationStep(
            description=f"计算距离：{b} - {middle} = {distance}，{middle} - {a} = {distance}",
            operation="计算距离",
            result=f"距离为{distance}"
        ))
        
        # 计算中间数的平方
        middle_square = middle ** 2
        steps.append(CalculationStep(
            description=f"中间数平方：{middle}² = {middle_square}",
            operation="计算中间数平方",
            result=middle_square
        ))
        
        # 计算距离的平方
        distance_square = distance ** 2
        steps.append(CalculationStep(
            description=f"距离平方：{distance}² = {distance_square}",
            operation="计算距离平方",
            result=distance_square
        ))
        
        # 计算最终结果
        final_result = middle_square - distance_square
        if final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{middle_square} - {distance_square} = {final_result}",
            operation="计算差值",
            result=final_result,
            formula="差额法：(m+d)(m-d) = m² - d²，其中m为中间数，d为距离"
        ))
        
        return steps