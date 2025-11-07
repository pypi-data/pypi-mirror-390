"""
乘以11实现
两位数及以上数乘11，两边一拉，中间相加，满十进一
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByEleven(MathCalculator):
    """乘以11算法"""
    
    def __init__(self):
        super().__init__("乘11速算", "两位数及以上乘11，两边一拉中间相加", priority=4)
        self.formula = "(10xa+b)x11=ax100+(a+b)x10+b"
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两位数及以上乘以11"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, int) and isinstance(b, int)):
                return False
            
            # 检查是否有一个数是11，另一个数是两位数及以上
            if a == 11 and abs(b) >= 10:
                return True
            elif b == 11 and abs(a) >= 10:
                return True
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建乘11速算步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 确定哪个是11，哪个是被乘数
        if a == 11:
            multiplied_num = abs(b)
            is_negative = b < 0
        else:
            multiplied_num = abs(a)
            is_negative = a < 0
        
        str_num = str(multiplied_num)
        digits = list(map(int, str_num))
        n = len(digits)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{multiplied_num} × 11 使用乘11速算法",
            operation="识别模式",
            result="两边一拉，中间相加，满十进位"
        ))
        
        steps.append(CalculationStep(
            description=f"原数各位数字：{' '.join(str_num)}",
            operation="数字分解",
            result=f"从左到右：{', '.join(str_num)}"
        ))
        
        # 乘11速算法的核心：两边一拉，中间相加
        # 对于数字 abc，结果构建为 a|(a+b)|(b+c)|c
        
        raw_result = []
        addition_details = []
        
        # 第一位：保持不变
        raw_result.append(digits[0])
        addition_details.append(f"首位：{digits[0]}")
        
        # 中间各位：相邻数字相加
        for i in range(n - 1):
            sum_val = digits[i] + digits[i + 1]
            raw_result.append(sum_val)
            addition_details.append(f"{digits[i]} + {digits[i+1]} = {sum_val}")
        
        # 最后一位：保持不变
        raw_result.append(digits[-1])
        addition_details.append(f"末位：{digits[-1]}")
        
        steps.append(CalculationStep(
            description=f"两边一拉中间相加：{'; '.join(addition_details)}",
            operation="构建初步结果",
            result=f"得到：{' | '.join(map(str, raw_result))}"
        ))
        
        # 处理进位：从右向左
        final_digits = []
        carry = 0
        carry_process = []
        
        for i in range(len(raw_result) - 1, -1, -1):
            total = raw_result[i] + carry
            if total >= 10:
                carry = total // 10
                digit = total % 10
                final_digits.insert(0, digit)
                carry_process.append(f"{raw_result[i]}+{total-raw_result[i]}={total} → {digit}(进位{carry})")
            else:
                carry = 0
                digit = total
                final_digits.insert(0, digit)
                if raw_result[i] != total:
                    carry_process.append(f"{raw_result[i]}+{total-raw_result[i]}={total}")
        
        if carry > 0:
            final_digits.insert(0, carry)
        
        if any(x >= 10 for x in raw_result):
            steps.append(CalculationStep(
                description=f"处理进位：{'; '.join(reversed(carry_process))}",
                operation="进位调整",
                result="从右向左处理满十进位"
            ))
        
        # 构建最终结果
        final_result = int(''.join(map(str, final_digits)))
        if is_negative:
            final_result = -final_result
        
        steps.append(CalculationStep(
            description=f"最终结果：{final_result}",
            operation="完成计算",
            result=final_result,
            formula="乘11法则：两边一拉，中间相加，满十进一"
        ))
        
        return steps