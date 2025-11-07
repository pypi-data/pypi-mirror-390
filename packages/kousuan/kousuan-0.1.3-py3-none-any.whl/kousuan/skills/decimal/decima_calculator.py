"""
小数计算通用算子
实现小数的加减乘除基本运算规则
"""

from typing import List, Tuple
from decimal import Decimal, ROUND_HALF_UP
from ..base_types import MathCalculator, Formula, CalculationStep, ElementType


class DecimaCalculator(MathCalculator):
    """小数计算通用算子"""
    
    def __init__(self, name="小数计算", description="小数的加减乘除运算", priority=3):
        super().__init__(name, description, priority)
        self.decimal_precision = 4  # 默认精度
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：包含小数的四则运算"""
        if formula.type not in ["addition", "subtraction", "multiplication", "division"]:
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            # 检查是否至少有一个小数
            has_decimal = False
            for elem in numbers:
                value = elem.get_numeric_value()
                if isinstance(value, float) and not value.is_integer():
                    has_decimal = True
                    break
                # 检查字符串表示是否包含小数点
                if hasattr(elem, 'text') and '.' in str(elem.text):
                    has_decimal = True
                    break
            
            return has_decimal
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建小数计算步骤"""
        if formula.type == "addition":
            return self._construct_addition_steps(formula)
        elif formula.type == "subtraction":
            return self._construct_subtraction_steps(formula)
        elif formula.type == "multiplication":
            return self._construct_multiplication_steps(formula)
        elif formula.type == "division":
            return self._construct_division_steps(formula)
        else:
            return []
    
    def _construct_addition_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建小数加法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 步骤1：对齐小数点
        a_str, b_str = self._align_decimals(a, b)
        steps.append(CalculationStep(
            description=f"对齐小数点：{a} + {b} → {a_str} + {b_str}",
            operation="对齐小数点",
            result=f"{a_str} + {b_str}"
        ))
        
        # 步骤2：按整数相加
        a_int = int(a_str.replace('.', ''))
        b_int = int(b_str.replace('.', ''))
        sum_int = a_int + b_int
        
        steps.append(CalculationStep(
            description=f"按整数相加：{a_int} + {b_int} = {sum_int}",
            operation="整数相加",
            result=sum_int
        ))
        
        # 步骤3：恢复小数点
        decimal_places = len(a_str.split('.')[1]) if '.' in a_str else 0
        final_result = sum_int / (10 ** decimal_places)
        
        steps.append(CalculationStep(
            description=f"恢复小数点：{sum_int} → {final_result}",
            operation="恢复小数点",
            result=final_result,
            formula="小数加法 = 对齐小数点 → 整数相加 → 恢复小数点"
        ))
        
        return steps
    
    def _construct_subtraction_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建小数减法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 步骤1：对齐小数点
        a_str, b_str = self._align_decimals(a, b)
        steps.append(CalculationStep(
            description=f"对齐小数点：{a} - {b} → {a_str} - {b_str}",
            operation="对齐小数点",
            result=f"{a_str} - {b_str}"
        ))
        
        # 步骤2：按整数相减
        a_int = int(a_str.replace('.', ''))
        b_int = int(b_str.replace('.', ''))
        diff_int = a_int - b_int
        
        steps.append(CalculationStep(
            description=f"按整数相减：{a_int} - {b_int} = {diff_int}",
            operation="整数相减",
            result=diff_int
        ))
        
        # 步骤3：恢复小数点
        decimal_places = len(a_str.split('.')[1]) if '.' in a_str else 0
        final_result = diff_int / (10 ** decimal_places)
        
        steps.append(CalculationStep(
            description=f"恢复小数点：{diff_int} → {final_result}",
            operation="恢复小数点",
            result=final_result,
            formula="小数减法 = 对齐小数点 → 整数相减 → 恢复小数点"
        ))
        
        return steps
    
    def _construct_multiplication_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建小数乘法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 步骤1：记录小数位数
        a_str, b_str = str(a), str(b)
        p1 = len(a_str.split('.')[1]) if '.' in a_str else 0
        p2 = len(b_str.split('.')[1]) if '.' in b_str else 0
        total_places = p1 + p2
        
        steps.append(CalculationStep(
            description=f"记录小数位数：{a}有{p1}位，{b}有{p2}位，共{total_places}位",
            operation="统计小数位数",
            result=f"总小数位数：{total_places}"
        ))
        
        # 步骤2：去小数点按整数相乘
        a_int = int(a_str.replace('.', ''))
        b_int = int(b_str.replace('.', ''))
        product_int = a_int * b_int
        
        steps.append(CalculationStep(
            description=f"整数相乘：{a_int} × {b_int} = {product_int}",
            operation="整数相乘",
            result=product_int
        ))
        
        # 步骤3：移动小数点
        final_result = product_int / (10 ** total_places)
        
        steps.append(CalculationStep(
            description=f"移动小数点{total_places}位：{product_int} → {final_result}",
            operation="移动小数点",
            result=final_result,
            formula="小数乘法位数 = 因数1小数位数 + 因数2小数位数"
        ))
        
        return steps
    
    def _construct_division_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建小数除法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        steps = []
        
        # 步骤1：统计除数小数位数
        b_str = str(b)
        decimal_places = len(b_str.split('.')[1]) if '.' in b_str else 0
        
        if decimal_places > 0:
            steps.append(CalculationStep(
                description=f"除数{b}有{decimal_places}位小数，需要化为整数",
                operation="分析除数",
                result=f"需要移动{decimal_places}位小数点"
            ))
            
            # 步骤2：同时移动小数点
            scale_factor = 10 ** decimal_places
            a_scaled = a * scale_factor
            b_scaled = b * scale_factor
            
            steps.append(CalculationStep(
                description=f"同时扩大{scale_factor}倍：{a} ÷ {b} → {a_scaled} ÷ {b_scaled}",
                operation="化除数为整数",
                result=f"{a_scaled} ÷ {b_scaled}"
            ))
        else:
            a_scaled, b_scaled = a, b
            steps.append(CalculationStep(
                description=f"除数{b}已是整数，直接计算",
                operation="除数分析",
                result=f"{a} ÷ {b}"
            ))
        
        # 步骤3：执行除法
        final_result = a_scaled / b_scaled
        
        steps.append(CalculationStep(
            description=f"执行除法：{a_scaled} ÷ {b_scaled} = {final_result}",
            operation="执行除法",
            result=final_result,
            formula="小数除法 = 除数化整数 → 同时移动小数点 → 执行除法"
        ))
        
        return steps
    
    def _align_decimals(self, a: float, b: float) -> Tuple[str, str]:
        """对齐小数点，短的补零"""
        a_str, b_str = str(a), str(b)
        
        # 获取小数位数
        a_places = len(a_str.split('.')[1]) if '.' in a_str else 0
        b_places = len(b_str.split('.')[1]) if '.' in b_str else 0
        
        # 统一小数位数
        max_places = max(a_places, b_places)
        
        if '.' not in a_str:
            a_str += '.' + '0' * max_places
        else:
            a_str += '0' * (max_places - a_places)
            
        if '.' not in b_str:
            b_str += '.' + '0' * max_places
        else:
            b_str += '0' * (max_places - b_places)
        
        return a_str, b_str
    
    def _format_decimal_result(self, result: float) -> float:
        """格式化小数结果，去除不必要的尾随零"""
        # 使用 Decimal 进行精确计算
        decimal_result = Decimal(str(result)).quantize(
            Decimal('0.0001'), rounding=ROUND_HALF_UP
        )
        return float(decimal_result)
