"""
一般乘法实现
支持逐位相乘法的通用乘法算法，包括特殊规则处理、负数和小数支持
"""

from typing import List, Union
from decimal import Decimal, getcontext
from fractions import Fraction
from ..base_types import MathCalculator, Formula, CalculationStep

# 设置小数精度
getcontext().prec = 28


class GeneralMultiplication(MathCalculator):
    """一般乘法算法（逐位相乘法）"""
    
    def __init__(self):
        super().__init__("一般乘法", "通用乘法", priority=1)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：所有乘法运算（最低优先级，兜底算法）"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            factor1, factor2 = [elem.get_numeric_value() for elem in numbers]
            # 支持整数、浮点数
            return isinstance(factor1, (int, float)) and isinstance(factor2, (int, float))
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建一般乘法步骤"""
        numbers = formula.get_numbers()
        factor1 = numbers[0].get_numeric_value()
        factor2 = numbers[1].get_numeric_value()
        
        # 转换Fraction为float以便处理
        if isinstance(factor1, Fraction):
            factor1 = float(factor1)
        if isinstance(factor2, Fraction):
            factor2 = float(factor2)
        
        # 检查特殊情况（按优先级顺序）
        if factor1 == 0 or factor2 == 0:
            self.name = "零乘法"
            self.priority = 9
            return self._construct_zero_multiplication_steps(factor1, factor2)
        elif factor1 == 1 or factor2 == 1:
            self.name = "一乘法"
            self.priority = 9
            return self._construct_one_multiplication_steps(factor1, factor2)
        elif self._is_single_digit_multiplication(factor1, factor2):
            self.name = "表内乘法"
            self.priority = 9
            return self._construct_single_digit_steps(factor1, factor2)
        elif isinstance(factor1, float) or isinstance(factor2, float):
            return self._construct_decimal_steps(factor1, factor2)
        elif factor1 < 0 or factor2 < 0:
            return self._construct_negative_steps(factor1, factor2)
        else:
            return self._construct_general_steps(int(factor1), int(factor2))
    
    def _is_single_digit_multiplication(self, factor1: Union[int, float], factor2: Union[int, float]) -> bool:
        """判断是否为两个个位数的乘法"""
        return (isinstance(factor1, int) and isinstance(factor2, int) and 
                1 <= factor1 <= 9 and 1 <= factor2 <= 9)
    
    def _construct_zero_multiplication_steps(self, factor1: Union[int, float], factor2: Union[int, float]) -> List[CalculationStep]:
        """构建0乘法的特殊步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{factor1} × {factor2} = 0",
            operation="0乘法规律",
            result=0,
            formula="0与任何数相乘都等于0"
        ))
        
        return steps
    
    def _construct_one_multiplication_steps(self, factor1: Union[int, float], factor2: Union[int, float]) -> List[CalculationStep]:
        """构建1乘法的特殊步骤"""
        steps = []
        
        result = factor2 if factor1 == 1 else factor1
        steps.append(CalculationStep(
            description=f"{factor1} × {factor2} = {result}",
            operation="1乘法规律",
            result=result,
            formula="1与任何数相乘都等于原数本身"
        ))
        
        return steps
    
    def _construct_single_digit_steps(self, factor1: int, factor2: int) -> List[CalculationStep]:
        """构建个位数乘法步骤（使用乘法口诀）"""
        steps = []
        result = factor1 * factor2
        
        # 构建乘法口诀
        multiplication_table = {
            (1, 1): "一一得一", (1, 2): "一二得二", (1, 3): "一三得三", (1, 4): "一四得四", 
            (1, 5): "一五得五", (1, 6): "一六得六", (1, 7): "一七得七", (1, 8): "一八得八", (1, 9): "一九得九",
            (2, 2): "二二得四", (2, 3): "二三得六", (2, 4): "二四得八", (2, 5): "二五一十", 
            (2, 6): "二六十二", (2, 7): "二七74", (2, 8): "二八十六", (2, 9): "二九十八",
            (3, 3): "三三得九", (3, 4): "三四十二", (3, 5): "三五55", (3, 6): "三六68", 
            (3, 7): "三七二十一", (3, 8): "三八二十四", (3, 9): "三九二十七",
            (4, 4): "四四十六", (4, 5): "四五二十", (4, 6): "四六二十四", (4, 7): "四七二十八", 
            (4, 8): "四八三十二", (4, 9): "四九三十六",
            (5, 5): "五五二十五", (5, 6): "五六三十", (5, 7): "五七三十五", (5, 8): "五八四十", (5, 9): "五九四十五",
            (6, 6): "六六三十六", (6, 7): "六七四十二", (6, 8): "六八四十八", (6, 9): "六九五十四",
            (7, 7): "七七四十九", (7, 8): "七八五十六", (7, 9): "七九六十三",
            (8, 8): "八八六十四", (8, 9): "八九七十二",
            (9, 9): "九九八十一"
        }
        
        # 获取口诀（确保顺序正确）
        key = (min(factor1, factor2), max(factor1, factor2))
        formula_text = multiplication_table.get(key, f"{factor1}×{factor2}={result}")
        
        steps.append(CalculationStep(
            description=f"{factor1} × {factor2} = {result}",
            operation="表内乘法口诀",
            result=result,
            formula=formula_text
        ))
        
        return steps
        
    def _construct_negative_steps(self, factor1: Union[int, float], factor2: Union[int, float]) -> List[CalculationStep]:
        """构建负数乘法步骤"""
        steps = []
        
        # 判断符号
        is_factor1_negative = factor1 < 0
        is_factor2_negative = factor2 < 0
        result_positive = not (is_factor1_negative ^ is_factor2_negative)  # 异或取反
        
        abs_factor1 = abs(factor1)
        abs_factor2 = abs(factor2)
        
        steps.append(CalculationStep(
            description=f"{factor1} × {factor2} 处理负数乘法",
            operation="分析符号",
            result="负数乘法：同号为正，异号为负"
        ))
        
        steps.append(CalculationStep(
            description=f"符号分析：{factor1} {'< 0' if is_factor1_negative else '> 0'}, {factor2} {'< 0' if is_factor2_negative else '> 0'}",
            operation="确定结果符号",
            result=f"结果为{'正数' if result_positive else '负数'}"
        ))
        
        steps.append(CalculationStep(
            description=f"取绝对值：|{factor1}| = {abs_factor1}, |{factor2}| = {abs_factor2}",
            operation="计算绝对值",
            result=f"计算 {abs_factor1} × {abs_factor2}"
        ))
        
        # 递归处理绝对值乘法
        abs_result = abs_factor1 * abs_factor2
        
        if isinstance(abs_factor1, int) and isinstance(abs_factor2, int):
            # 整数情况，展示逐位相乘
            steps.extend(self._construct_digit_multiplication_steps(abs_factor1, abs_factor2, int(abs_result)))
        else:
            # 小数情况，简化处理
            steps.append(CalculationStep(
                description=f"{abs_factor1} × {abs_factor2} = {abs_result}",
                operation="计算绝对值乘积",
                result=abs_result
            ))
        
        final_result = abs_result if result_positive else -abs_result
        steps.append(CalculationStep(
            description=f"添加符号：{abs_result} → {final_result}",
            operation="确定最终结果",
            result=final_result,
            formula="负数乘法：(-a) × (-b) = ab, (-a) × b = -ab"
        ))
        
        return steps
    
    def _construct_decimal_steps(self, factor1: Union[int, float], factor2: Union[int, float]) -> List[CalculationStep]:
        """构建小数乘法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{factor1} × {factor2} 处理小数乘法",
            operation="识别小数",
            result="小数乘法：先按整数相乘，再确定小数点位置"
        ))
        
        # 转换为字符串以便处理小数点
        str1 = str(factor1)
        str2 = str(factor2)
        
        decimal_places1 = len(str1.split('.')[1]) if '.' in str1 else 0
        decimal_places2 = len(str2.split('.')[1]) if '.' in str2 else 0
        total_decimal_places = decimal_places1 + decimal_places2
        
        steps.append(CalculationStep(
            description=f"小数位数：{factor1} 有 {decimal_places1} 位小数，{factor2} 有 {decimal_places2} 位小数",
            operation="统计小数位数",
            result=f"结果应有 {total_decimal_places} 位小数"
        ))
        
        # 转换为整数计算
        multiplier1 = 10 ** decimal_places1
        multiplier2 = 10 ** decimal_places2
        int_factor1 = int(factor1 * multiplier1)
        int_factor2 = int(factor2 * multiplier2)
        
        if decimal_places1 > 0 or decimal_places2 > 0:
            steps.append(CalculationStep(
                description=f"转换为整数：{factor1} × {multiplier1} = {int_factor1}, {factor2} × {multiplier2} = {int_factor2}",
                operation="消除小数点",
                result=f"计算 {int_factor1} × {int_factor2}"
            ))
        
        int_result = int_factor1 * int_factor2
        
        # 如果是小整数，展示逐位相乘
        if int_factor1 < 1000 and int_factor2 < 1000:
            steps.extend(self._construct_digit_multiplication_steps(int_factor1, int_factor2, int_result))
        else:
            steps.append(CalculationStep(
                description=f"{int_factor1} × {int_factor2} = {int_result}",
                operation="整数相乘",
                result=int_result
            ))
        
        final_result = factor1 * factor2
        if total_decimal_places > 0:
            steps.append(CalculationStep(
                description=f"确定小数点位置：{int_result} ÷ {10**total_decimal_places} = {final_result}",
                operation="还原小数点",
                result=final_result,
                formula="小数乘法：结果小数位数 = 两因数小数位数之和"
            ))
        else:
            steps.append(CalculationStep(
                description=f"最终结果：{final_result}",
                operation="确定结果",
                result=final_result
            ))
        
        return steps
    
    def _construct_general_steps(self, factor1: int, factor2: int) -> List[CalculationStep]:
        """构建一般整数乘法步骤"""
        steps = []
        
        steps.append(CalculationStep(
            description=f"{factor1} × {factor2} 使用逐位相乘法",
            operation="识别一般乘法",
            result="按照位数逐位相乘，再按权相加"
        ))
        
        result = factor1 * factor2
        steps.extend(self._construct_digit_multiplication_steps(factor1, factor2, result))
        
        return steps
    
    def _construct_digit_multiplication_steps(self, factor1: int, factor2: int, expected_result: int) -> List[CalculationStep]:
        """构建逐位相乘的详细步骤"""
        steps = []
        
        # 将因数按位分解
        str1 = str(abs(factor1))
        str2 = str(abs(factor2))
        
        # 选择较小的数作为乘数，较大的数作为被乘数（提高效率）
        if len(str2) < len(str1):
            factor1, factor2 = factor2, factor1
            str1, str2 = str2, str1
        
        steps.append(CalculationStep(
            description=f"分解乘数：{factor2} 按位分解进行逐位相乘",
            operation="分解乘数",
            result=f"以 {factor1} 为被乘数，{factor2} 为乘数"
        ))
        
        partial_products = []
        
        # 逐位相乘
        for i, digit2 in enumerate(reversed(str2)):
            digit_val = int(digit2)
            position_value = 10 ** i
            
            if digit_val == 0:
                partial_product = 0
                steps.append(CalculationStep(
                    description=f"{factor1} × {digit_val} × {position_value} = 0（个位为0）",
                    operation=f"第{i+1}位相乘",
                    result=0
                ))
            else:
                basic_product = factor1 * digit_val
                partial_product = basic_product * position_value
                
                steps.append(CalculationStep(
                    description=f"{factor1} × {digit_val}（{position_value}位）= {factor1} × {digit_val} × {position_value} = {partial_product}",
                    operation=f"第{i+1}位相乘",
                    result=partial_product
                ))
            
            partial_products.append(partial_product)
        
        # 显示部分积
        if len(partial_products) > 1:
            non_zero_products = [p for p in partial_products if p != 0]
            steps.append(CalculationStep(
                description=f"部分积：{' + '.join(map(str, non_zero_products))}",
                operation="列出所有部分积",
                result=f"需要将这些部分积相加"
            ))
            
            # 逐步相加
            running_sum = 0
            for i, product in enumerate(partial_products):
                if product != 0:
                    running_sum += product
                    if i == 0:
                        steps.append(CalculationStep(
                            description=f"累加：{product}",
                            operation="开始累加",
                            result=running_sum
                        ))
                    else:
                        steps.append(CalculationStep(
                            description=f"累加：{running_sum - product} + {product} = {running_sum}",
                            operation="继续累加",
                            result=running_sum
                        ))
        
        final_result = sum(partial_products)
        steps.append(CalculationStep(
            description=f"最终结果：{factor1} × {factor2} = {final_result}",
            operation="完成计算",
            result=final_result,
            formula="逐位相乘法：(AB) × C = A×10×C + B×C"
        ))
        
        return steps