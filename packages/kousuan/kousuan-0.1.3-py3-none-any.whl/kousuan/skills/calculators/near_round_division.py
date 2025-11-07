"""
近整十除法实现
处理接近整十数的除法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class NearRoundDivision(MathCalculator):
    """近整十除法算法"""
    
    def __init__(self):
        super().__init__("近整十除法", "近整十，先估后调", priority=5)
    
    def _find_nearest_round(self, num: int) -> int:
        """找到最接近的整十数"""
        return round(num / 10) * 10
    
    def _find_nearest_hundred(self, num: int) -> int:
        """找到最接近的整百数"""
        return round(num / 100) * 100
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被除数接近整十数或整百数"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        # 如果被除数是5的倍数，可使用更高阶方法
        if numbers[0].get_numeric_value() % 5 == 0:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(dividend, int) and isinstance(divisor, int)):
                return False
            
            if divisor == 0:
                return False
            
            # 除数应该是单位数，便于心算
            if divisor > 12 or divisor < 2:
                return False
            
            # 检查被除数是否接近整十数
            nearest_ten = self._find_nearest_round(dividend)
            diff_ten = abs(dividend - nearest_ten)
            
            # 检查被除数是否接近整百数
            nearest_hundred = self._find_nearest_hundred(dividend)
            diff_hundred = abs(dividend - nearest_hundred)
            
            # 如果接近整十数（差值在5以内）或整百数（差值在20以内）
            is_near_ten = diff_ten <= 5 and nearest_ten != dividend and nearest_ten >= 10
            is_near_hundred = diff_hundred <= 20 and nearest_hundred != dividend and nearest_hundred >= 100
            
            return is_near_ten or is_near_hundred
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建近整十除法步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        # 确保是整数
        dividend_int = int(dividend)
        divisor_int = int(divisor)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别近整十除法：{dividend_int} ÷ {divisor_int}",
            operation="识别模式",
            result="近整十，先估后调"
        ))
        
        # 选择最合适的基准数（整十或整百）
        nearest_ten = self._find_nearest_round(dividend_int)
        diff_ten = abs(dividend_int - nearest_ten)
        
        nearest_hundred = self._find_nearest_hundred(dividend_int)
        diff_hundred = abs(dividend_int - nearest_hundred)
        
        # 选择差值较小的基准数
        if diff_ten <= diff_hundred and nearest_ten >= 10:
            base_num = nearest_ten
            diff = dividend_int - base_num
            base_type = "整十数"
        else:
            base_num = nearest_hundred
            diff = dividend_int - base_num
            base_type = "整百数"
        
        steps.append(CalculationStep(
            description=f"选择最接近的{base_type}：{base_num}，差值为 {diff}",
            operation="选择基准",
            result=f"{dividend_int} = {base_num} + ({diff})"
        ))
        
        # 计算基准数的除法
        base_quotient = base_num / divisor_int
        
        steps.append(CalculationStep(
            description=f"先算基准数除法：{base_num} ÷ {divisor_int} = {base_quotient}",
            operation="基准计算",
            result=base_quotient
        ))
        
        # 计算差值的影响
        if diff != 0:
            diff_quotient = diff / divisor_int
            
            steps.append(CalculationStep(
                description=f"计算差值影响：{diff} ÷ {divisor_int} = {diff_quotient}",
                operation="差值计算",
                result=diff_quotient
            ))
            
            # 合并结果
            final_result = base_quotient + diff_quotient
            
            if diff > 0:
                steps.append(CalculationStep(
                    description=f"被除数比基准数大，加上差值：{base_quotient} + {diff_quotient} = {final_result}",
                    operation="调整结果",
                    result=final_result,
                    formula="近整数除法：基准数结果 + 差值结果"
                ))
            else:
                steps.append(CalculationStep(
                    description=f"被除数比基准数小，减去差值：{base_quotient} + {diff_quotient} = {final_result}",
                    operation="调整结果",
                    result=final_result,
                    formula="近整数除法：基准数结果 + 差值结果"
                ))
        else:
            final_result = base_quotient
            steps.append(CalculationStep(
                description=f"无需调整，结果就是：{final_result}",
                operation="确定结果",
                result=final_result
            ))
        
        # 提供验证
        actual_result = dividend_int / divisor_int
        if abs(final_result - actual_result) < 0.001:
            steps.append(CalculationStep(
                description=f"验证：{dividend_int} ÷ {divisor_int} = {final_result}",
                operation="验证正确",
                result="✓ 计算正确"
            ))
        else:
            steps.append(CalculationStep(
                description=f"精确结果：{dividend_int} ÷ {divisor_int} = {actual_result}",
                operation="精确计算",
                result=actual_result
            ))
        
        return steps