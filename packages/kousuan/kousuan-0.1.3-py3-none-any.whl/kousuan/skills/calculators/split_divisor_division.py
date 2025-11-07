"""
拆分除数法实现
将除数拆成两个更容易计算的因数，然后连续除
"""

from typing import List, Tuple
from ..base_types import MathCalculator, Formula, CalculationStep


class SplitDivisorDivision(MathCalculator):
    """拆分除数法算法"""
    
    def __init__(self):
        super().__init__("拆分除数法", "除数拆因数，连续除", priority=5)
    
    def _find_factor_pairs(self, num: int) -> List[Tuple[int, int]]:
        """找到一个数的所有因数对"""
        factors = []
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                factors.append((i, num // i))
        return factors
    
    def _evaluate_factor_pair(self, dividend, factor1: int, factor2: int) -> int:
        """评估因数对的计算难易程度（分数越低越容易）"""
        score = 0
        
        # 因数大小评分（越小越好）
        score += (factor1 - 2) + (factor2 - 2)
        
        # 特殊数字加分（2, 3, 4, 5, 8, 10等更容易）
        easy_numbers = {2, 3, 4, 5, 8, 10, 12, 15, 16, 20, 25}
        if factor1 in easy_numbers:
            score -= 5
        if factor2 in easy_numbers:
            score -= 5
        
        # 如果被除数能被第一个因数整除，优先
        if isinstance(dividend, (int, float)) and dividend % factor1 == 0:
            score -= 10
        
        return score
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：除数可以被有效拆分"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            
            if not isinstance(divisor, (int, float)):
                return False
            
            # 除数必须是整数且大于等于6
            if isinstance(divisor, float):
                if not divisor.is_integer():
                    return False
                divisor = int(divisor)
            
            if divisor < 6:
                return False
            
            # 排除质数（无法有效拆分）
            if divisor in [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
                return False
            
            # 排除10的幂（有专门算法）
            if str(divisor)[0] == '1' and all(d == '0' for d in str(divisor)[1:]):
                return False
            
            # 排除2的幂（有专门算法）
            if divisor > 0 and (divisor & (divisor - 1)) == 0:
                return False
            
            # 排除5, 25, 125（有专门算法）
            if divisor in [5, 25, 125]:
                return False
            
            # 必须有合适的因数分解
            factor_pairs = self._find_factor_pairs(divisor)
            return len(factor_pairs) > 0
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建拆分除数法步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        # 确保除数是整数
        if isinstance(divisor, float) and divisor.is_integer():
            divisor = int(divisor)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 使用拆分除数法",
            operation="识别模式",
            result="除数拆因数，连续除"
        ))
        
        # 找到所有因数对
        factor_pairs = self._find_factor_pairs(int(divisor))
        
        # 选择最优的因数对
        best_pair = min(factor_pairs, key=lambda pair: self._evaluate_factor_pair(dividend, pair[0], pair[1]))
        factor1, factor2 = best_pair
        
        # 显示可选的拆分方案
        if len(factor_pairs) > 1:
            factor_descriptions = [f"{divisor} = {p[0]} × {p[1]}" for p in factor_pairs]
            steps.append(CalculationStep(
                description=f"可能的拆分方案：{'; '.join(factor_descriptions)}",
                operation="分析拆分",
                result=f"选择最优方案：{divisor} = {factor1} × {factor2}"
            ))
        else:
            steps.append(CalculationStep(
                description=f"拆分除数：{divisor} = {factor1} × {factor2}",
                operation="拆分除数",
                result=f"先除以{factor1}，再除以{factor2}"
            ))
        
        # 第一步除法
        intermediate_result = dividend / factor1
        
        steps.append(CalculationStep(
            description=f"第一步：{dividend} ÷ {factor1} = {intermediate_result}",
            operation="第一次除法",
            result=intermediate_result
        ))
        
        # 第二步除法
        final_result = intermediate_result / factor2
        
        steps.append(CalculationStep(
            description=f"第二步：{intermediate_result} ÷ {factor2} = {final_result}",
            operation="第二次除法",
            result=final_result
        ))
        
        # 如果结果是整数，显示为整数
        if isinstance(final_result, float) and final_result.is_integer():
            final_result = int(final_result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ {divisor} = {final_result}",
            operation="确定结果",
            result=final_result,
            formula="拆分除数法：a ÷ (b×c) = a ÷ b ÷ c"
        ))
        
        # 验证结果
        verification = final_result * divisor
        if abs(verification - dividend) < 0.001:
            steps.append(CalculationStep(
                description=f"验证：{final_result} × {divisor} = {verification}",
                operation="验证正确",
                result="✓ 计算正确"
            ))
        
        # 提供心算技巧
        if divisor <= 100:
            steps.append(CalculationStep(
                description=f"心算技巧：记住{divisor} = {factor1} × {factor2}，遇到除以{divisor}就分两步",
                operation="心算提示",
                result=f"常用拆分：{divisor} = {factor1} × {factor2}"
            ))
        
        return steps