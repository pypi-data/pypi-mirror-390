"""
接近100的两位数相乘实现
两个接近100的数相乘，使用补数简化计算
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class NearHundredMultiplication(MathCalculator):
    """接近100的两位数相乘"""
    
    def __init__(self):
        super().__init__("接近100数相乘", "接近100的数相乘（80-120范围），使用补数简化计算", priority=2)
    
    def _is_near_hundred(self, num) -> tuple:
        """检查是否接近100，返回(是否接近, 补数)"""
        num = int(num)
        # 扩大适用范围：补数绝对值小于20，即80-120范围内
        if 80 <= num <= 120:
            complement = 100 - num
            return True, complement
        return False, 0
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个接近100的数相乘"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 两个数都必须接近100
            is_near_a, _ = self._is_near_hundred(a)
            is_near_b, _ = self._is_near_hundred(b)
            
            return is_near_a and is_near_b
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建接近100数相乘步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 计算补数
        _, complement_a = self._is_near_hundred(a)
        _, complement_b = self._is_near_hundred(b)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别接近100的数：{a} 和 {b}",
            operation="识别模式",
            result="使用接近100数相乘公式"
        ))
        
        # 显示补数
        steps.append(CalculationStep(
            description=f"{a} 的补数：{complement_a}，{b} 的补数：{complement_b}",
            operation="计算补数",
            result=f"a={complement_a}, b={complement_b}"
        ))
        
        # 应用公式 (100-a)(100-b) = 10000 - 100(a+b) + ab
        sum_complements = complement_a + complement_b
        product_complements = complement_a * complement_b
        
        # 处理补数和的显示
        if complement_a < 0 and complement_b < 0:
            sum_description = f"补数和：({complement_a}) + ({complement_b}) = {sum_complements}"
        elif complement_a < 0:
            sum_description = f"补数和：({complement_a}) + {complement_b} = {sum_complements}"
        elif complement_b < 0:
            sum_description = f"补数和：{complement_a} + ({complement_b}) = {sum_complements}"
        else:
            sum_description = f"补数和：{complement_a} + {complement_b} = {sum_complements}"
        
        steps.append(CalculationStep(
            description=sum_description,
            operation="计算补数和",
            result=sum_complements
        ))
        
        # 处理补数积的显示
        if complement_a < 0 and complement_b < 0:
            product_description = f"补数积：({complement_a}) × ({complement_b}) = {product_complements}"
        elif complement_a < 0:
            product_description = f"补数积：({complement_a}) × {complement_b} = {product_complements}"
        elif complement_b < 0:
            product_description = f"补数积：{complement_a} × ({complement_b}) = {product_complements}"
        else:
            product_description = f"补数积：{complement_a} × {complement_b} = {product_complements}"
        
        steps.append(CalculationStep(
            description=product_description,
            operation="计算补数积",
            result=product_complements
        ))
        
        # 计算最终结果
        # 方法：(100-a)(100-b) = 10000 - 100(a+b) + ab
        hundred_times_sum = 100 * sum_complements
        intermediate = 10000 - hundred_times_sum
        final_result = intermediate + product_complements
        
        # 构建公式显示，处理负数情况
        if sum_complements < 0:
            sum_part = f"({sum_complements})"
        else:
            sum_part = str(sum_complements)
        
        if product_complements < 0:
            product_part = f"({product_complements})"
        else:
            product_part = str(product_complements)
        
        steps.append(CalculationStep(
            description=f"应用公式：10000 - 100×{sum_part} + {product_part}",
            operation="应用公式",
            result=f"10000 - {hundred_times_sum} + {product_complements}" if hundred_times_sum >= 0 else f"10000 - ({hundred_times_sum}) + {product_complements}"
        ))
        
        # 处理最终计算步骤的显示
        if hundred_times_sum < 0 and product_complements < 0:
            # 两个都是负数：10000 - (-200) + (-15) = 10000 + 200 - 15
            calculation_display = f"= 10000 - ({hundred_times_sum}) + ({product_complements}) = 10000 + {-hundred_times_sum} - {-product_complements} = {final_result}"
        elif hundred_times_sum < 0:
            # 只有第一个是负数：10000 - (-200) + 15 = 10000 + 200 + 15
            calculation_display = f"= 10000 - ({hundred_times_sum}) + {product_complements} = 10000 + {-hundred_times_sum} + {product_complements} = {final_result}"
        elif product_complements < 0:
            # 只有第二个是负数：10000 - 200 + (-15) = 10000 - 200 - 15
            calculation_display = f"= 10000 - {hundred_times_sum} + ({product_complements}) = 10000 - {hundred_times_sum} - {-product_complements} = {final_result}"
        else:
            # 都是正数
            calculation_display = f"= {intermediate} + {product_complements} = {final_result}"
        
        steps.append(CalculationStep(
            description=calculation_display,
            operation="计算结果",
            result=final_result,
            formula="(100-a)(100-b) = 10000 - 100(a+b) + ab"
        ))
        
        return steps