"""
商不变性质实现（同乘同除法）
被除数和除数同时乘以或除以同一个不为0的数，商不变
主要用于简化小数除法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep
from fractions import Fraction


class QuotientInvariantDivision(MathCalculator):
    """商不变性质算法（同乘同除法）"""
    
    def __init__(self):
        super().__init__("商不变性质", "同乘同除，商不变", priority=3)
    
    def _find_simplification_factor(self, dividend, divisor) -> int:
        """寻找合适的简化因子"""
        # 优先处理小数转整数
        if isinstance(divisor, float):
            decimal_places = len(str(divisor).split('.')[-1])
            return 10 ** decimal_places
        
        if isinstance(dividend, float):
            decimal_places = len(str(dividend).split('.')[-1])
            return 10 ** decimal_places
        
        # 处理整数的公因数
        if isinstance(dividend, int) and isinstance(divisor, int):
            # 寻找最大公因数
            import math
            gcd = math.gcd(abs(dividend), abs(divisor))
            if gcd > 1:
                return gcd
        
        return 1
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：包含小数的除法或有公因数的除法"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if divisor == 0:
                return False
            
            # 情况1：除数是小数（需要转换为整数）
            if isinstance(divisor, float) and not divisor.is_integer():
                return True
            
            # 情况2：被除数是小数（可以简化）
            if isinstance(dividend, float) and not dividend.is_integer():
                return True
            
            # 情况3：被除数和除数都是整数且有公因数（可以约分）
            if isinstance(dividend, int) and isinstance(divisor, int):
                import math
                gcd = math.gcd(abs(dividend), abs(divisor))
                if gcd > 1:
                    return True
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建商不变性质步骤"""
        numbers = formula.get_numbers()
        dividend = numbers[0].get_numeric_value()
        divisor = numbers[1].get_numeric_value()
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{dividend} ÷ {divisor} 使用商不变性质",
            operation="识别模式",
            result="同乘同除，商不变"
        ))
        
        # 判断处理策略
        if isinstance(divisor, float) and not divisor.is_integer():
            # 策略1：除数是小数，转换为整数
            decimal_places = len(str(divisor).split('.')[-1])
            multiplier = 10 ** decimal_places
            
            new_dividend = dividend * multiplier
            new_divisor = divisor * multiplier
            
            steps.append(CalculationStep(
                description=f"除数是小数，同乘以{multiplier}消除小数点",
                operation="消除小数",
                result=f"被除数和除数都乘以{multiplier}"
            ))
            
            steps.append(CalculationStep(
                description=f"({dividend} × {multiplier}) ÷ ({divisor} × {multiplier}) = {new_dividend} ÷ {int(new_divisor)}",
                operation="同乘转换",
                result=f"{new_dividend} ÷ {int(new_divisor)}"
            ))
            
            # 计算结果
            result = new_dividend / new_divisor
            
            steps.append(CalculationStep(
                description=f"{new_dividend} ÷ {int(new_divisor)} = {result}",
                operation="整数除法",
                result=result
            ))
            
        elif isinstance(dividend, float) and not dividend.is_integer():
            # 策略2：被除数是小数，可以优化
            decimal_places = len(str(dividend).split('.')[-1])
            multiplier = 10 ** decimal_places
            
            new_dividend = dividend * multiplier
            new_divisor = divisor * multiplier
            
            steps.append(CalculationStep(
                description=f"被除数是小数，同乘以{multiplier}简化计算",
                operation="简化小数",
                result=f"被除数和除数都乘以{multiplier}"
            ))
            
            steps.append(CalculationStep(
                description=f"({dividend} × {multiplier}) ÷ ({divisor} × {multiplier}) = {int(new_dividend)} ÷ {int(new_divisor)}",
                operation="同乘转换",
                result=f"{int(new_dividend)} ÷ {int(new_divisor)}"
            ))
            
            # 计算结果
            result = new_dividend / new_divisor
            
            steps.append(CalculationStep(
                description=f"{int(new_dividend)} ÷ {int(new_divisor)} = {result}",
                operation="整数除法",
                result=result
            ))
            
        else:
            # 策略3：整数约分
            import math
            gcd = math.gcd(abs(int(dividend)), abs(int(divisor)))
            
            new_dividend = int(dividend) // gcd
            new_divisor = int(divisor) // gcd
            
            steps.append(CalculationStep(
                description=f"找到最大公因数：{gcd}",
                operation="寻找公因数",
                result=f"{dividend} 和 {divisor} 的最大公因数是 {gcd}"
            ))
            
            steps.append(CalculationStep(
                description=f"同除以{gcd}进行约分",
                operation="约分简化",
                result=f"被除数和除数都除以{gcd}"
            ))
            
            steps.append(CalculationStep(
                description=f"({dividend} ÷ {gcd}) ÷ ({divisor} ÷ {gcd}) = {new_dividend} ÷ {new_divisor}",
                operation="约分结果",
                result=f"{new_dividend} ÷ {new_divisor}"
            ))
            
            # 计算结果
            result = new_dividend / new_divisor
            
            if new_divisor == 1:
                steps.append(CalculationStep(
                    description=f"{new_dividend} ÷ 1 = {new_dividend}",
                    operation="除以1",
                    result=new_dividend
                ))
                result = new_dividend
            else:
                steps.append(CalculationStep(
                    description=f"{new_dividend} ÷ {new_divisor} = {result}",
                    operation="简化除法",
                    result=result
                ))
        
        # 如果结果是整数，显示为整数
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        
        steps.append(CalculationStep(
            description=f"最终结果：{dividend} ÷ {divisor} = {result}",
            operation="确定结果",
            result=result,
            formula="商不变性质：(a×k) ÷ (b×k) = a ÷ b"
        ))
        
        return steps