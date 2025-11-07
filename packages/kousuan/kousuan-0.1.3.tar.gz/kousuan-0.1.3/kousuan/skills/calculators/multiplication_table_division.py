"""
九九表速算除法实现
利用乘法表反推除法
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplicationTableDivision(MathCalculator):
    """九九表速算除法算法"""
    
    def __init__(self):
        super().__init__("九九表速算", "熟表反推，除数快算", priority=4)
    
    def _multiplication_table(self) -> dict:
        """生成九九乘法表"""
        table = {}
        for i in range(1, 10):
            for j in range(1, 10):
                table[i * j] = (i, j)
        return table
    
    def _extended_table(self) -> dict:
        """生成扩展乘法表（包括12以内的乘法）"""
        table = {}
        for i in range(1, 13):
            for j in range(1, 13):
                product = i * j
                if product not in table:
                    table[product] = []
                table[product].append((i, j))
        return table
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：能在九九表或扩展表中找到的除法"""
        if formula.type != "division":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            dividend, divisor = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(dividend, int) and isinstance(divisor, int)):
                return False
            
            if divisor == 0 or divisor == 1:  # 排除除数为1的情况
                return False
            
            # 除数必须在2-12范围内（常见乘法表范围）
            if divisor < 2 or divisor > 12:
                return False
            
            # 被除数必须能整除除数
            if dividend % divisor != 0:
                return False
            
            quotient = dividend // divisor
            
            # 商也必须在1-12范围内
            if quotient < 1 or quotient > 12:
                return False
            
            # 被除数应该在扩展乘法表范围内（最大144）
            return dividend <= 144
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建九九表速算除法步骤"""
        numbers = formula.get_numbers()
        dividend, divisor = [elem.get_numeric_value() for elem in numbers]
        
        # 确保是整数
        dividend_int = int(dividend)
        divisor_int = int(divisor)
        
        quotient = dividend_int // divisor_int
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"识别九九表速算：{dividend_int} ÷ {divisor_int}",
            operation="识别模式",
            result="熟表反推，除数快算"
        ))
        
        # 判断使用哪个乘法表
        if dividend_int <= 81 and divisor_int <= 9 and quotient <= 9:
            table_type = "九九乘法表"
        else:
            table_type = "扩展乘法表"
        
        steps.append(CalculationStep(
            description=f"使用{table_type}反推：{divisor_int} × ? = {dividend_int}",
            operation="反推思路",
            result=f"寻找 {divisor_int} 的倍数等于 {dividend_int}"
        ))
        
        # 展示思维过程
        if divisor_int <= 9:
            # 展示该数在乘法表中的倍数
            multiples = []
            for i in range(1, min(10, dividend_int // divisor_int + 2)):
                multiple = divisor_int * i
                if multiple == dividend_int:
                    multiples.append(f"{divisor_int}×{i}={multiple} ✓")
                elif multiple <= dividend_int + divisor_int:
                    multiples.append(f"{divisor_int}×{i}={multiple}")
            
            steps.append(CalculationStep(
                description=f"{divisor_int}的倍数：{' '.join(multiples[:4])}",
                operation="列举倍数",
                result=f"找到：{divisor_int} × {quotient} = {dividend_int}"
            ))
        
        # 直接给出答案
        steps.append(CalculationStep(
            description=f"根据乘法表：{divisor_int} × {quotient} = {dividend_int}",
            operation="表查结果",
            result=quotient
        ))
        
        steps.append(CalculationStep(
            description=f"因此：{dividend_int} ÷ {divisor_int} = {quotient}",
            operation="得出答案",
            result=quotient,
            formula="九九表反推：a × b = c，则 c ÷ a = b"
        ))
        
        # 如果是经典九九表范围，添加口诀提示
        if dividend_int <= 81 and divisor_int <= 9 and quotient <= 9:
            if quotient <= divisor_int:
                steps.append(CalculationStep(
                    description=f"乘法口诀：{quotient}×{divisor_int}={dividend_int}",
                    operation="口诀验证",
                    result=f"背诵口诀帮助快速计算"
                ))
            else:
                steps.append(CalculationStep(
                    description=f"乘法口诀：{divisor_int}×{quotient}={dividend_int}",
                    operation="口诀验证",
                    result=f"背诵口诀帮助快速计算"
                ))
        
        return steps