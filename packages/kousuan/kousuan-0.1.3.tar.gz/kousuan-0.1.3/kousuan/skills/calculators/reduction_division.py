"""
约分法除法实现
被除数和除数有公因数时，先同时除以它们的最大公因数
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep
import math


class ReductionDivision(MathCalculator):
    """约分法除法算法"""
    
    def __init__(self):
        super().__init__("约分法", "找公因数，先约分", priority=3)
    
    def _find_common_factors(self, a: int, b: int) -> List[int]:
        """找到两个数的所有公因数"""
        gcd = math.gcd(abs(a), abs(b))
        factors = []
        
        for i in range(1, int(gcd**0.5) + 1):
            if gcd % i == 0 and i != b and i != 1:
                factors.append(i)
                if i != gcd // i:
                    factors.append(gcd // i)
        
        return sorted(set(factors), reverse=True)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：被除数和除数都是整数，且有公因数大于1"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            
            # 必须都是整数
            if not (isinstance(dividend, int) and isinstance(divisor, int)):
                return False
            
            if divisor == 0:
                return False
            
            # 必须有大于1的公因数,且公因数不能是除数本身
            gcd = math.gcd(abs(dividend), abs(divisor))
            # 公因数判断难度较高，限制gcd为5或2的倍数
            if gcd % 5 != 0 and gcd % 2 != 0:
                return False
            gcc = self._find_common_factors(dividend, divisor)
            return gcd > 1 and len(gcc) > 0
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建约分法除法步骤"""
        numbers = formula.get_numbers()
        dividend = int(numbers[0].get_numeric_value())
        divisor = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 使用约分法",
            operation="识别整数除法",
            result="找公因数，先约分"
        ))
        
        # 找到所有公因数
        common_factors = self._find_common_factors(dividend, divisor)

        gcd = 1
        if len(common_factors) > 0:
            gcd = common_factors[0]  # 最大公因数
        
        if len(common_factors) > 2:  # 有多个公因数（除了1和最大公因数）
            steps.append(CalculationStep(
                description=f"寻找公因数：{dividend} 和 {divisor} 的公因数有 {common_factors}",
                operation="寻找公因数",
                result=f"最大公因数是 {gcd}"
            ))
        else:
            steps.append(CalculationStep(
                description=f"计算最大公因数：gcd({dividend}, {divisor}) = {gcd}",
                operation="计算最大公因数",
                result=f"最大公因数是 {gcd}"
            ))
        
        # 展示约分过程
        new_dividend = dividend // gcd
        new_divisor = divisor // gcd
        
        steps.append(CalculationStep(
            description=f"同时除以最大公因数{gcd}进行约分",
            operation="约分操作",
            result=f"{dividend} ÷ {gcd} = {new_dividend}, {divisor} ÷ {gcd} = {new_divisor}"
        ))
        
        steps.append(CalculationStep(
            description=f"约分后：{dividend} ÷ {divisor} = {new_dividend} ÷ {new_divisor}",
            operation="约分结果",
            result=f"{new_dividend} ÷ {new_divisor}"
        ))
        
        # 计算最终结果
        if new_divisor == 1:
            final_result = new_dividend
            steps.append(CalculationStep(
                description=f"{new_dividend} ÷ 1 = {new_dividend}",
                operation="除以1",
                result=final_result
            ))
        else:
            final_result = new_dividend / new_divisor
            
            if isinstance(final_result, float) and final_result.is_integer():
                final_result = int(final_result)
                steps.append(CalculationStep(
                    description=f"{new_dividend} ÷ {new_divisor} = {final_result}",
                    operation="整除计算",
                    result=final_result
                ))
            else:
                steps.append(CalculationStep(
                    description=f"{new_dividend} ÷ {new_divisor} = {final_result}",
                    operation="除法计算",
                    result=final_result
                ))
        
        # 提供分数形式（如果适用）
        if new_divisor > 1 and new_divisor <= 20:
            steps.append(CalculationStep(
                description=f"分数形式：{dividend} ÷ {divisor} = {new_dividend}/{new_divisor}",
                operation="分数表示",
                result=f"最简分数：{new_dividend}/{new_divisor}"
            ))
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ {divisor} = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="约分法：(a×k) ÷ (b×k) = a ÷ b"
        ))
        
        # 提供验证
        verification = final_result * divisor
        if abs(verification - dividend) < 0.001:
            steps.append(CalculationStep(
                description=f"验证：{final_result} × {divisor} = {verification}",
                operation="验证正确",
                result="✓ 计算正确"
            ))
        
        return steps