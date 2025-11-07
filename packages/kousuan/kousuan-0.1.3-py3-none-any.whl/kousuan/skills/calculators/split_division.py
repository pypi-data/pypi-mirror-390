"""
拆分除法实现
将被除数拆分为方便计算的和，再分别除以除数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SplitDivision(MathCalculator):
    """拆分除法算法"""
    
    def __init__(self):
        super().__init__("拆分除法", "拆分除，再相加", priority=4)
    
    def _find_split_candidates(self, dividend: int, divisor: int) -> List[tuple]:
        """找到合适的拆分方案"""
        candidates = []

        # 策略1：按整十数拆分
        if dividend >= 10:
            tens_part = (dividend // 10) * 10
            ones_part = dividend % 10
            
            if tens_part > 0 and ones_part >= 0:
                # 检查是否能整除
                tens_quotient = tens_part / divisor
                ones_quotient = ones_part / divisor
                
                # 优先选择能整除的拆分
                if tens_part % divisor == 0 or ones_part % divisor == 0:
                    candidates.append((tens_part, ones_part, "整十数拆分", 1))
                else:
                    candidates.append((tens_part, ones_part, "整十数拆分", 3))
        
        # 策略2：按倍数拆分（寻找除数的倍数）
        for multiplier in range(1, dividend // divisor + 1):
            multiple = divisor * multiplier
            if multiple < dividend:
                remainder = dividend - multiple
                if remainder > 0:
                    # 完美倍数拆分，优先级最高
                    candidates.append((multiple, remainder, f"{divisor}的{multiplier}倍拆分", 0))
        
        # 策略3：按相近数值拆分（使两部分接近）
        if dividend > divisor * 2:
            half = dividend // 2
            # 找到最接近一半且便于计算的拆分点
            for offset in range(min(10, half)):
                part1 = half + offset
                part2 = dividend - part1
                if part1 > 0 and part2 > 0:
                    candidates.append((part1, part2, "均匀拆分", 5))
                
                if offset > 0:
                    part1 = half - offset
                    part2 = dividend - part1
                    if part1 > 0 and part2 > 0:
                        candidates.append((part1, part2, "均匀拆分", 5))
        
        # 按优先级排序
        candidates.sort(key=lambda x: (x[3], abs(x[0] - x[1])))
        return candidates[:3]  # 返回最好的3个候选
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被除数可以有效拆分的除法"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        ## 如果被除数是5的倍数，可使用更高阶方法
        if dividend % 5 == 0:
            return False
        
        ## 如果结果是10的倍数，可使用更高阶方法
        if divisor != 0 and dividend % (divisor * 10) == 0:
            return False
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(dividend, int) and isinstance(divisor, int)):
                return False
            
            if divisor == 0 or dividend <= 0:
                return False
            
            # 被除数应该足够大，适合拆分（至少是除数的2倍以上）
            if dividend < divisor * 2:
                return False
            
            # 被除数应该小于1000（避免过于复杂）
            if dividend > 999:
                return False
            
            # 除数应该是单位数或两位数（便于心算）
            if divisor > 99:
                return False
            
            # 检查是否有合适的拆分方案
            candidates = self._find_split_candidates(dividend, divisor)
            return len(candidates) > 0
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建拆分除法步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        # 确保是整数
        dividend_int = int(dividend)
        divisor_int = int(divisor)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别拆分除法：{dividend_int} ÷ {divisor_int}",
            operation="识别模式",
            result="拆分除，再相加"
        ))
        
        # 找到最佳拆分方案
        candidates = self._find_split_candidates(dividend_int, divisor_int)
        if not candidates:
            # 如果没有找到拆分方案，使用默认拆分
            part1 = (dividend_int // 10) * 10
            part2 = dividend_int % 10
            split_method = "默认拆分"
        else:
            part1, part2, split_method, _ = candidates[0]
        
        steps.append(CalculationStep(
            description=f"选择拆分方案（{split_method}）：{dividend_int} = {part1} + {part2}",
            operation="确定拆分",
            result=f"{dividend_int} = {part1} + {part2}"
        ))
        
        # 分别计算两部分的除法
        quotient1 = part1 / divisor_int
        quotient2 = part2 / divisor_int
        
        steps.append(CalculationStep(
            description=f"分别计算：{part1} ÷ {divisor_int} = {quotient1}",
            operation="第一部分",
            result=quotient1
        ))
        
        steps.append(CalculationStep(
            description=f"分别计算：{part2} ÷ {divisor_int} = {quotient2}",
            operation="第二部分",
            result=quotient2
        ))
        
        # 合并结果
        final_result = quotient1 + quotient2
        
        steps.append(CalculationStep(
            description=f"合并结果：{quotient1} + {quotient2} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="拆分除法：(A+B) ÷ C = A ÷ C + B ÷ C"
        ))
        
        # 如果结果是分数，提供额外说明
        if isinstance(final_result, float) and not final_result.is_integer():
            steps.append(CalculationStep(
                description=f"验证：{dividend_int} ÷ {divisor_int} = {final_result}",
                operation="验证结果",
                result=f"结果为小数：{final_result}"
            ))
        
        return steps