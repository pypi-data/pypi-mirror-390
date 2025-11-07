"""
由高到低位法减法实现
从最高位开始，逐位相减，适用于无需借位的减法
符合心算习惯的通用减法方法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class HighToLowDigitSubtraction(MathCalculator):
    """由高到低位法减法算法"""
    
    def __init__(self):
        super().__init__("由高到低位法减法", "按数位从高到低顺序计算，符合心算习惯", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：适用于不需要借位的多位数减法"""
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
            
            # 适用于两位数及以上的减法，且被减数大于减数
            if minuend < 10 or subtrahend < 10 or minuend <= subtrahend:
                return False
            
            # 检查是否需要借位（如果需要借位，优先级应该较低）
            return not self._needs_borrowing(minuend, subtrahend)
            
        except:
            return False
    
    def _needs_borrowing(self, minuend: int, subtrahend: int) -> bool:
        """检查是否需要借位"""
        minuend_str = str(minuend)
        subtrahend_str = str(subtrahend).zfill(len(minuend_str))
        
        for i in range(len(minuend_str)):
            if int(minuend_str[i]) < int(subtrahend_str[i]):
                return True
        return False
    
    def _get_digit_breakdown(self, number: int) -> List[tuple]:
        """将数字按位分解，返回(位名称, 位值, 数值)的列表"""
        if number == 0:
            return [("个位", 0, 0)]
        
        digits = []
        position_names = ["个位", "十位", "百位", "千位", "万位"]
        position = 0
        temp = number
        
        while temp > 0 and position < len(position_names):
            digit = temp % 10
            place_value = digit * (10 ** position)
            if digit > 0:  # 只记录非零位
                digits.append((position_names[position], digit, place_value))
            temp //= 10
            position += 1
        
        # 返回从高位到低位的顺序
        return list(reversed(digits))
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建由高到低位法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用由高到低位法",
            operation="识别算法",
            result="按位从高到低顺序计算"
        ))
        
        # 分解两个数字
        breakdown_minuend = self._get_digit_breakdown(minuend)
        breakdown_subtrahend = self._get_digit_breakdown(subtrahend)
        
        breakdown_minuend_str = " + ".join([f"{val}" for _, _, val in breakdown_minuend])
        breakdown_subtrahend_str = " + ".join([f"{val}" for _, _, val in breakdown_subtrahend])
        
        steps.append(CalculationStep(
            description=f"数字分解",
            operation="按位分解",
            result=f"{minuend} = {breakdown_minuend_str}；{subtrahend} = {breakdown_subtrahend_str}"
        ))
        
        # 合并同级位数，从高位到低位
        all_positions = {}
        
        # 收集被减数的所有位的值
        for pos_name, digit, place_value in breakdown_minuend:
            if pos_name not in all_positions:
                all_positions[pos_name] = [0, 0]
            all_positions[pos_name][0] = place_value
        
        # 收集减数的所有位的值
        for pos_name, digit, place_value in breakdown_subtrahend:
            if pos_name not in all_positions:
                all_positions[pos_name] = [0, 0]
            all_positions[pos_name][1] = place_value
        
        # 按位次顺序处理（从高到低）
        position_order = ["万位", "千位", "百位", "十位", "个位"]
        partial_results = []
        
        for pos_name in position_order:
            if pos_name in all_positions:
                val1, val2 = all_positions[pos_name]
                if val1 > 0 or val2 > 0:
                    pos_diff = val1 - val2
                    if pos_diff != 0:
                        partial_results.append(pos_diff)
                        
                        if val1 > 0 and val2 > 0:
                            steps.append(CalculationStep(
                                description=f"{pos_name}相减：{val1} - {val2} = {pos_diff}",
                                operation=f"{pos_name}计算",
                                result=pos_diff
                            ))
                        elif val1 > 0:
                            steps.append(CalculationStep(
                                description=f"{pos_name}：{val1}（减数此位为0）",
                                operation=f"{pos_name}计算",
                                result=val1
                            ))
        
        # 合并所有位的结果
        if len(partial_results) > 1:
            final_result = sum(partial_results)
            partial_str = " + ".join([str(x) for x in partial_results])
            steps.append(CalculationStep(
                description=f"合并各位结果：{partial_str} = {final_result}",
                operation="合并结果",
                result=final_result,
                formula="由高到低位法：分位计算后合并"
            ))
        else:
            final_result = partial_results[0] if partial_results else 0
            steps.append(CalculationStep(
                description=f"最终结果：{final_result}",
                operation="确认结果",
                result=final_result,
                formula="由高到低位法：分位计算后合并"
            ))
        
        return steps