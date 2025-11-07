"""
由高到低位法加法实现
按照数位从高到低的顺序进行加法计算，先算十位、百位等高位，再算个位等低位
这是最通用和直观的心算方法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class HighToLowDigitAddition(MathCalculator):
    """由高到低位法加法算法"""
    
    def __init__(self):
        super().__init__("由高到低位法", "按数位从高到低顺序计算，符合心算习惯的通用加法方法", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：适用于所有多位数加法（两位数及以上）"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, (int, float)) and isinstance(addend2, (int, float))):
                return False
            
            # 转换为整数
            addend1, addend2 = int(addend1), int(addend2)
            
            # 适用于两位数及以上的加法
            return addend1 >= 10 and addend2 >= 10
        except:
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
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用由高到低位法",
            operation="识别算法",
            result="按位从高到低顺序计算"
        ))
        
        # 分解两个数字
        breakdown1 = self._get_digit_breakdown(addend1)
        breakdown2 = self._get_digit_breakdown(addend2)
        
        breakdown1_str = " + ".join([f"{val}" for _, _, val in breakdown1])
        breakdown2_str = " + ".join([f"{val}" for _, _, val in breakdown2])
        
        steps.append(CalculationStep(
            description=f"数字分解",
            operation="按位分解",
            result=f"{addend1} = {breakdown1_str}；{addend2} = {breakdown2_str}"
        ))
        
        # 合并同级位数，从高位到低位
        all_positions = {}
        
        # 收集所有位的值
        for pos_name, digit, place_value in breakdown1:
            if pos_name not in all_positions:
                all_positions[pos_name] = [0, 0]
            all_positions[pos_name][0] = place_value
        
        for pos_name, digit, place_value in breakdown2:
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
                    pos_sum = val1 + val2
                    partial_results.append(pos_sum)
                    
                    if val1 > 0 and val2 > 0:
                        steps.append(CalculationStep(
                            description=f"{pos_name}相加：{val1} + {val2} = {pos_sum}",
                            operation=f"{pos_name}计算",
                            result=pos_sum
                        ))
                    elif val1 > 0:
                        steps.append(CalculationStep(
                            description=f"{pos_name}：{val1}（仅第一个数有此位）",
                            operation=f"{pos_name}计算",
                            result=val1
                        ))
                    else:
                        steps.append(CalculationStep(
                            description=f"{pos_name}：{val2}（仅第二个数有此位）",
                            operation=f"{pos_name}计算",
                            result=val2
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