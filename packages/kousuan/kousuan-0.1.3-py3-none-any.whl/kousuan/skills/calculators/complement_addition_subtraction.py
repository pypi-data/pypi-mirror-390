"""
补数加减法实现
接近整十、整百的数的加减法，先当作整十、整百数计算，再调整
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ComplementAdditionSubtraction(MathCalculator):
    """补数加减法"""
    
    def __init__(self):
        super().__init__("补数加减法", "接近整十、整百的数的加减法", priority=2)
    
    def _find_nearest_round_number(self, num) -> tuple:
        """找到最接近的整十或整百数"""
        # 转换为整数
        num = int(num)
        
        # 检查是否接近整十数
        tens = (num // 10 + 1) * 10 if num % 10 >= 5 else (num // 10) * 10
        tens_diff = abs(num - tens)
        
        # 检查是否接近整百数
        hundreds = (num // 100 + 1) * 100 if num % 100 >= 50 else (num // 100) * 100
        hundreds_diff = abs(num - hundreds)
        
        # 选择差值较小的作为目标整数
        if tens_diff <= hundreds_diff and tens_diff <= 5:  # 放宽到5以内
            return tens, tens_diff, "十"
        elif hundreds_diff <= 10:  # 放宽到10以内
            return hundreds, hundreds_diff, "百"
        else:
            return None, None, None
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：至少有一个数接近整十或整百数"""
        if formula.type not in ["addition", "subtraction"]:
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否有数接近整十或整百
            round_a, diff_a, type_a = self._find_nearest_round_number(a)
            round_b, diff_b, type_b = self._find_nearest_round_number(b)
            
            return (round_a is not None) or (round_b is not None)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建补数加减法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        operation = "+" if formula.type == "addition" else "-"
        
        # 找出接近整十或整百的数
        round_a, diff_a, type_a = self._find_nearest_round_number(a)
        round_b, diff_b, type_b = self._find_nearest_round_number(b)
        
        steps = []
        
        if formula.type == "addition":
            # 加法：将接近整十、整百的数先当作整十、整百数相加，再减去多加的部分
            if round_a is not None and (round_b is None or diff_a <= diff_b):
                # 使用a的补数
                target_num, complement, unit_type = round_a, diff_a, type_a
                direction = "多加了" if a < target_num else "少加了"
                adjust_op = "-" if a < target_num else "+"
                
                steps.append(CalculationStep(
                    description=f"将 {a} 看作整{unit_type}数 {target_num}（{direction} {complement}）",
                    operation="识别补数",
                    result=f"{a} ≈ {target_num}"
                ))
                
                temp_result = target_num + b
                steps.append(CalculationStep(
                    description=f"计算 {target_num} + {b} = {temp_result}",
                    operation="整数计算",
                    result=temp_result
                ))
                
                final_result = temp_result - complement if a < target_num else temp_result + complement
                steps.append(CalculationStep(
                    description=f"{direction} {complement}，需要{adjust_op}{complement}：{temp_result} {adjust_op} {complement} = {final_result}",
                    operation="调整结果",
                    result=final_result
                ))
                
            elif round_b is not None:
                # 使用b的补数
                target_num, complement, unit_type = round_b, diff_b, type_b
                direction = "多加了" if b < target_num else "少加了"
                adjust_op = "-" if b < target_num else "+"
                
                steps.append(CalculationStep(
                    description=f"将 {b} 看作整{unit_type}数 {target_num}（{direction} {complement}）",
                    operation="识别补数",
                    result=f"{b} ≈ {target_num}"
                ))
                
                temp_result = a + target_num
                steps.append(CalculationStep(
                    description=f"计算 {a} + {target_num} = {temp_result}",
                    operation="整数计算",
                    result=temp_result
                ))
                
                final_result = temp_result - complement if b < target_num else temp_result + complement
                steps.append(CalculationStep(
                    description=f"{direction} {complement}，需要{adjust_op}{complement}：{temp_result} {adjust_op} {complement} = {final_result}",
                    operation="调整结果",
                    result=final_result
                ))
        
        else:  # subtraction
            # 减法：将接近整十、整百的数先当作整十、整百数相减，再调整
            if round_b is not None:
                # 被减数使用b的补数
                target_num, complement, unit_type = round_b, diff_b, type_b
                if b < target_num:
                    # b小于目标数，我们用更大的数减，所以多减了
                    direction = "多减了"
                    adjust_op = "+"  # 需要加回差值
                else:
                    # b大于目标数，我们用更小的数减，所以少减了
                    direction = "少减了"
                    adjust_op = "-"  # 需要再减去差值
                
                steps.append(CalculationStep(
                    description=f"将 {b} 看作整{unit_type}数 {target_num}（{direction} {complement}）",
                    operation="识别补数",
                    result=f"{b} ≈ {target_num}"
                ))
                
                temp_result = a - target_num
                steps.append(CalculationStep(
                    description=f"计算 {a} - {target_num} = {temp_result}",
                    operation="整数计算",
                    result=temp_result
                ))
                
                final_result = temp_result + complement if b < target_num else temp_result - complement
                steps.append(CalculationStep(
                    description=f"{direction} {complement}，需要{adjust_op}{complement}：{temp_result} {adjust_op} {complement} = {final_result}",
                    operation="调整结果",
                    result=final_result
                ))
        
        return steps