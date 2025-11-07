"""
整十除法实现
处理整十数、整百数、整千数的除法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class RoundNumberDivision(MathCalculator):
    """整十除法算法"""
    
    def __init__(self):
        super().__init__("整十除法", "去零心算快，整十除得易", priority=6)
    
    def _count_trailing_zeros(self, num: int) -> int:
        """统计数字末尾的0个数"""
        if num == 0:
            return 1
        count = 0
        while num % 10 == 0:
            count += 1
            num //= 10
        return count
    
    def _remove_trailing_zeros(self, num: int) -> int:
        """去掉数字末尾的0"""
        while num % 10 == 0 and num != 0:
            num //= 10
        return num
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被除数和除数都是整十数（末尾有0）"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(dividend, int) and isinstance(divisor, int)):
                return False
            
            if divisor == 0:
                return False
            
            # 检查是否都是整十数（除数必须是整十数，被除数也必须是整十数）
            divisor_zeros = self._count_trailing_zeros(divisor)
            dividend_zeros = self._count_trailing_zeros(dividend)
            
            # 除数必须是整十数（至少一个0），被除数也必须是整十数
            return divisor_zeros >= 1 and dividend_zeros >= 1 and divisor >= 10 and dividend >= 10
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建整十除法步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        # 确保是整数
        dividend_int = int(dividend)
        divisor_int = int(divisor)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别整十除法：{dividend_int} ÷ {divisor_int}",
            operation="识别模式",
            result="去零心算快，整十除得易"
        ))
        
        # 统计零的个数
        dividend_zeros = self._count_trailing_zeros(dividend_int)
        divisor_zeros = self._count_trailing_zeros(divisor_int)
        
        # 去掉零后的数字
        dividend_no_zeros = self._remove_trailing_zeros(dividend_int)
        divisor_no_zeros = self._remove_trailing_zeros(divisor_int)
        
        steps.append(CalculationStep(
            description=f"分析零的个数：{dividend_int} 末尾有 {dividend_zeros} 个0，{divisor_int} 末尾有 {divisor_zeros} 个0",
            operation="分析位数",
            result=f"去零后：{dividend_no_zeros} ÷ {divisor_no_zeros}"
        ))
        
        # 计算去零后的除法
        base_result = dividend_no_zeros / divisor_no_zeros
        
        steps.append(CalculationStep(
            description=f"先算去零后的除法：{dividend_no_zeros} ÷ {divisor_no_zeros} = {base_result}",
            operation="基础计算",
            result=base_result
        ))
        
        # 处理剩余的零
        remaining_zeros = dividend_zeros - divisor_zeros
        
        if remaining_zeros > 0:
            final_result = base_result * (10 ** remaining_zeros)
            steps.append(CalculationStep(
                description=f"被除数多 {remaining_zeros} 个0，结果乘以 10^{remaining_zeros}：{base_result} × {10**remaining_zeros} = {final_result}",
                operation="恢复位数",
                result=final_result,
                formula="整十除法：去零算，差几零补几零"
            ))
        elif remaining_zeros < 0:
            final_result = base_result / (10 ** abs(remaining_zeros))
            steps.append(CalculationStep(
                description=f"除数多 {abs(remaining_zeros)} 个0，结果除以 10^{abs(remaining_zeros)}：{base_result} ÷ {10**abs(remaining_zeros)} = {final_result}",
                operation="恢复位数",
                result=final_result,
                formula="整十除法：去零算，差几零除几零"
            ))
        else:
            final_result = base_result
            steps.append(CalculationStep(
                description=f"零的个数相同，结果就是：{final_result}",
                operation="确定结果",
                result=final_result,
                formula="整十除法：零数同，直接算"
            ))
        
        return steps