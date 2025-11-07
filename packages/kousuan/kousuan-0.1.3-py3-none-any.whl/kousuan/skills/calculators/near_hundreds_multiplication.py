"""
接近整百数的乘法实现
适用于接近任意整百数（100、200、300等）的数相乘，使用补数简化计算
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class NearHundredsMultiplication(MathCalculator):
    """接近整百数的乘法"""
    
    def __init__(self):
        super().__init__("接近整百数乘法", "接近整百数相乘，使用补数简化计算", priority=3)
        self.formula = "(N - a)(N - b) = N² - N(a + b) + ab"
    
    def _find_nearest_hundred(self, num) -> tuple:
        """找到最接近的整百数，返回(整百数, 补数)"""
        num = int(num)
        # 找到最接近的整百数
        nearest_hundred = round(num / 100) * 100
        if nearest_hundred == 0:
            nearest_hundred = 100
        
        complement = nearest_hundred - num
        
        # 只有当补数绝对值小于等于25时才认为接近
        if abs(complement) <= 25:
            return nearest_hundred, complement
        return None, 0
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个接近整百数的数相乘"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 尝试找到一个合适的整百数基准
            possible_bases = [100, 200, 300, 400, 500, 600]  # 可以根据需要扩展
            
            for base in possible_bases:
                comp_a = abs(base - a)
                comp_b = abs(base - b)
                # 两个补数都必须小于等于25，且至少有一个小于等于15
                if comp_a <= 25 and comp_b <= 25 and (comp_a <= 15 or comp_b <= 15):
                    return True
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建接近整百数乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 找到最接近的整百数
        nearest_a, complement_a = self._find_nearest_hundred(a)
        nearest_b, complement_b = self._find_nearest_hundred(b)
        
        # 选择更适合的基准整百数（选择让两个补数绝对值之和最小的）
        if nearest_a == nearest_b:
            base_hundred = nearest_a
        else:
            # 计算使用不同基准时的补数绝对值之和
            base_hundred_a = nearest_a
            base_hundred_b = nearest_b
            
            # 使用nearest_a作为基准时的补数绝对值之和
            comp_a_with_base_a = abs(base_hundred_a - a)
            comp_b_with_base_a = abs(base_hundred_a - b)
            total_diff_a = comp_a_with_base_a + comp_b_with_base_a
            
            # 使用nearest_b作为基准时的补数绝对值之和
            comp_a_with_base_b = abs(base_hundred_b - a)
            comp_b_with_base_b = abs(base_hundred_b - b)
            total_diff_b = comp_a_with_base_b + comp_b_with_base_b
            
            # 选择补数绝对值之和最小的基准
            if total_diff_a <= total_diff_b:
                base_hundred = base_hundred_a
            else:
                base_hundred = base_hundred_b
            
            # 如果选择的基准导致某个补数超过25，则不适用此算法
            comp_a_final = base_hundred - a
            comp_b_final = base_hundred - b
            if abs(comp_a_final) > 25 or abs(comp_b_final) > 25:
                # 尝试其他可能的基准
                possible_bases = [100, 200, 300, 400, 500]  # 可以扩展
                best_base = None
                min_total_diff = float('inf')
                
                for base in possible_bases:
                    comp_a_test = abs(base - a)
                    comp_b_test = abs(base - b)
                    if comp_a_test <= 25 and comp_b_test <= 25:
                        total_diff = comp_a_test + comp_b_test
                        if total_diff < min_total_diff:
                            min_total_diff = total_diff
                            best_base = base
                
                if best_base:
                    base_hundred = best_base
        
        # 重新计算基于选定基准的补数
        complement_a = base_hundred - a
        complement_b = base_hundred - b
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别接近整百数：{a} 和 {b} 都接近 {base_hundred}",
            operation="识别模式",
            result=f"使用接近{base_hundred}的乘法公式"
        ))
        
        # 显示补数
        steps.append(CalculationStep(
            description=f"{a} 距离 {base_hundred} 的补数：{complement_a}，{b} 距离 {base_hundred} 的补数：{complement_b}",
            operation="计算补数",
            result=f"a={complement_a}, b={complement_b}"
        ))
        
        # 应用公式：(base-comp_a)(base-comp_b) = base² - base(comp_a + comp_b) + comp_a×comp_b
        sum_complements = complement_a + complement_b
        product_complements = complement_a * complement_b
        base_squared = base_hundred * base_hundred
        
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
        hundred_times_sum = base_hundred * sum_complements
        intermediate = base_squared - hundred_times_sum
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
            description=f"应用公式：{base_squared} - {base_hundred}×{sum_part} + {product_part}",
            operation="应用公式",
            result=f"{base_squared} - {hundred_times_sum} + {product_complements}" if hundred_times_sum >= 0 else f"{base_squared} - ({hundred_times_sum}) + {product_complements}"
        ))
        
        # 处理最终计算步骤的显示
        if hundred_times_sum < 0 and product_complements < 0:
            calculation_display = f"= {base_squared} - ({hundred_times_sum}) + ({product_complements}) = {base_squared} + {-hundred_times_sum} - {-product_complements} = {final_result}"
        elif hundred_times_sum < 0:
            calculation_display = f"= {base_squared} - ({hundred_times_sum}) + {product_complements} = {base_squared} + {-hundred_times_sum} + {product_complements} = {final_result}"
        elif product_complements < 0:
            calculation_display = f"= {base_squared} - {hundred_times_sum} + ({product_complements}) = {base_squared} - {hundred_times_sum} - {-product_complements} = {final_result}"
        else:
            calculation_display = f"= {intermediate} + {product_complements} = {final_result}"
        
        steps.append(CalculationStep(
            description=calculation_display,
            operation="计算结果",
            result=final_result,
            formula=f"({base_hundred}-a)({base_hundred}-b) = {base_hundred}² - {base_hundred}(a+b) + ab"
        ))
        
        return steps