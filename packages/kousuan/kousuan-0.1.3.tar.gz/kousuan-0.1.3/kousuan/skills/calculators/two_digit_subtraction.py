"""
两位数减法的通用实现
根据数字特征自动选择最优算法：凑整法、破十法、直接减法等
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class TwoDigitSubtraction(MathCalculator):
    """两位数减法通用算法"""
    
    def __init__(self):
        super().__init__("两位数减法", "根据数字特征自动选择最优减法算法", priority=3)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两位数减法"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, int) and isinstance(subtrahend, int)):
                return False
            
            # 两位数减法：被减数和减数都是两位数，且结果为正
            return (10 <= minuend <= 99 and 10 <= subtrahend <= 99 and minuend >= subtrahend)
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建两位数减法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        # 判断使用哪种算法
        if self._is_adjacent_numbers(minuend, subtrahend):
            return self._construct_adjacent_steps(minuend, subtrahend)
        elif self._is_round_number_subtraction(minuend, subtrahend):
            return self._construct_round_number_steps(minuend, subtrahend)
        elif self._is_complement_to_round(subtrahend):
            return self._construct_complement_steps(minuend, subtrahend)
        elif self._needs_borrowing(minuend, subtrahend):
            return self._construct_borrowing_steps(minuend, subtrahend)
        else:
            return self._construct_direct_steps(minuend, subtrahend)
    
    def _is_adjacent_numbers(self, minuend: int, subtrahend: int) -> bool:
        """判断是否为相邻数相减"""
        return abs(minuend - subtrahend) == 1
    
    def _is_round_number_subtraction(self, minuend: int, subtrahend: int) -> bool:
        """判断是否为整十数减法"""
        return minuend % 10 == 0 and subtrahend % 10 == 0
    
    def _is_complement_to_round(self, subtrahend: int) -> bool:
        """判断减数是否接近整十（可用凑整法）"""
        ones = subtrahend % 10
        return ones >= 8 or ones <= 2  # 接近整十的情况
    
    def _needs_borrowing(self, minuend: int, subtrahend: int) -> bool:
        """判断是否需要借位"""
        minuend_ones = minuend % 10
        subtrahend_ones = subtrahend % 10
        return minuend_ones < subtrahend_ones
    
    def _construct_adjacent_steps(self, minuend: int, subtrahend: int) -> List[CalculationStep]:
        """构建相邻数减法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用相邻数规律",
            operation="识别相邻数",
            result="相邻数相减结果固定为1"
        ))
        
        result = minuend - subtrahend
        steps.append(CalculationStep(
            description=f"相邻数相减：{minuend} - {subtrahend} = {result}",
            operation="直接得出结果",
            result=result,
            formula="相邻数相减 = 1"
        ))
        
        return steps
    
    def _construct_round_number_steps(self, minuend: int, subtrahend: int) -> List[CalculationStep]:
        """构建整十数减法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用整十数减法",
            operation="识别整十数",
            result="整十数减法：先减十位，再补零"
        ))
        
        minuend_tens = minuend // 10
        subtrahend_tens = subtrahend // 10
        result_tens = minuend_tens - subtrahend_tens
        
        steps.append(CalculationStep(
            description=f"十位相减：{minuend_tens} - {subtrahend_tens} = {result_tens}",
            operation="计算十位差",
            result=result_tens
        ))
        
        result = result_tens * 10
        steps.append(CalculationStep(
            description=f"补零得到结果：{result_tens}0 = {result}",
            operation="补零",
            result=result,
            formula="整十数减法 = (十位相减)×10"
        ))
        
        return steps
    
    def _construct_complement_steps(self, minuend: int, subtrahend: int) -> List[CalculationStep]:
        """构建凑整法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用凑整法",
            operation="识别凑整机会",
            result="减数接近整十，先凑整再修正"
        ))
        
        # 找到最近的整十数
        round_number = ((subtrahend + 5) // 10) * 10
        difference = round_number - subtrahend
        
        steps.append(CalculationStep(
            description=f"将{subtrahend}凑整到{round_number}，差值为{difference}",
            operation="确定凑整数",
            result=f"凑整到{round_number}"
        ))
        
        temp_result = minuend - round_number
        steps.append(CalculationStep(
            description=f"先算：{minuend} - {round_number} = {temp_result}",
            operation="凑整计算",
            result=temp_result
        ))
        
        final_result = temp_result + difference
        steps.append(CalculationStep(
            description=f"修正结果：{temp_result} + {difference} = {final_result}",
            operation="修正差值",
            result=final_result,
            formula="凑整法：a - b = (a - round_b) + (round_b - b)"
        ))
        
        return steps
    
    def _construct_borrowing_steps(self, minuend: int, subtrahend: int) -> List[CalculationStep]:
        """构建借位减法步骤（破十法）"""
        steps = []
        
        minuend_tens = minuend // 10
        minuend_ones = minuend % 10
        subtrahend_tens = subtrahend // 10
        subtrahend_ones = subtrahend % 10
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用破十法",
            operation="识别借位需求",
            result="个位不够减，需要向十位借1"
        ))
        
        steps.append(CalculationStep(
            description=f"分解：{minuend} = {minuend_tens}0 + {minuend_ones}, {subtrahend} = {subtrahend_tens}0 + {subtrahend_ones}",
            operation="数字分解",
            result=f"被减数十位:{minuend_tens}，个位:{minuend_ones}；减数十位:{subtrahend_tens}，个位:{subtrahend_ones}"
        ))
        
        # 借位过程
        new_tens = minuend_tens - 1
        new_ones = minuend_ones + 10
        
        steps.append(CalculationStep(
            description=f"向十位借1：{minuend_tens}变成{new_tens}，{minuend_ones}变成{new_ones}",
            operation="借位操作",
            result=f"新的被减数：{new_tens}0 + {new_ones} = {new_tens * 10 + new_ones}"
        ))
        
        # 计算结果
        result_tens = new_tens - subtrahend_tens
        result_ones = new_ones - subtrahend_ones
        
        steps.append(CalculationStep(
            description=f"十位相减：{new_tens} - {subtrahend_tens} = {result_tens}",
            operation="计算十位",
            result=result_tens
        ))
        
        steps.append(CalculationStep(
            description=f"个位相减：{new_ones} - {subtrahend_ones} = {result_ones}",
            operation="计算个位",
            result=result_ones
        ))
        
        final_result = result_tens * 10 + result_ones
        steps.append(CalculationStep(
            description=f"组合结果：{result_tens}0 + {result_ones} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="破十法：借位后分别计算十位和个位"
        ))
        
        return steps
    
    def _construct_direct_steps(self, minuend: int, subtrahend: int) -> List[CalculationStep]:
        """构建直接减法步骤"""
        steps = []
        
        minuend_tens = minuend // 10
        minuend_ones = minuend % 10
        subtrahend_tens = subtrahend // 10
        subtrahend_ones = subtrahend % 10
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用直接减法",
            operation="识别直接减法",
            result="个位够减，直接计算"
        ))
        
        steps.append(CalculationStep(
            description=f"分解：{minuend} = {minuend_tens}0 + {minuend_ones}, {subtrahend} = {subtrahend_tens}0 + {subtrahend_ones}",
            operation="数字分解",
            result=f"十位:{minuend_tens}-{subtrahend_tens}，个位:{minuend_ones}-{subtrahend_ones}"
        ))
        
        result_tens = minuend_tens - subtrahend_tens
        result_ones = minuend_ones - subtrahend_ones
        
        steps.append(CalculationStep(
            description=f"十位相减：{minuend_tens} - {subtrahend_tens} = {result_tens}",
            operation="计算十位",
            result=result_tens
        ))
        
        steps.append(CalculationStep(
            description=f"个位相减：{minuend_ones} - {subtrahend_ones} = {result_ones}",
            operation="计算个位",
            result=result_ones
        ))
        
        final_result = result_tens * 10 + result_ones
        steps.append(CalculationStep(
            description=f"组合结果：{result_tens}0 + {result_ones} = {final_result}",
            operation="合并结果",
            result=final_result,
            formula="直接减法：分别计算十位和个位"
        ))
        
        return steps