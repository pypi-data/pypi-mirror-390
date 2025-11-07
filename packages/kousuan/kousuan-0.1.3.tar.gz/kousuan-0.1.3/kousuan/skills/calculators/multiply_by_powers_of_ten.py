"""
乘以10的幂实现 (补零法)
任何数乘以10, 100, 1000...，只需在数字后面添加相应个数的0
支持所有整零数：20, 30, 400, 500, 1000, 2000等
优化版本：同时分析两个乘数的零，统一处理
"""

from typing import List, Tuple
from ..base_types import MathCalculator, Formula, CalculationStep


class MultiplyByPowersOfTen(MathCalculator):
    """乘以10的幂算法 (补零法)"""
    
    def __init__(self):
        super().__init__("补零法", "乘以整十、整百、整千等数，利用补零规律简化计算", priority=5)
    
    def _analyze_zero_number(self, num) -> Tuple[bool, int, int]:
        """分析是否为整零数，返回(是否匹配, 非零部分, 零的个数)"""
        if not isinstance(num, int) or num <= 0:
            return False, 0, 0
        
        zero_count = 0
        temp = num
        
        # 计算末尾零的个数
        while temp % 10 == 0 and temp > 0:
            temp //= 10
            zero_count += 1
        
        # 如果有末尾零，说明是整零数
        return zero_count > 0, temp, zero_count
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：至少有一个整零数的乘法"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            a, b = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                return False
            
            # 检查是否有整零数
            is_zero_a, _, _ = self._analyze_zero_number(int(a)) if isinstance(a, int) else (False, 0, 0)
            is_zero_b, _, _ = self._analyze_zero_number(int(b)) if isinstance(b, int) else (False, 0, 0)
            
            return is_zero_a or is_zero_b
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建补零法步骤"""
        numbers = formula.get_numbers()
        a, b = [elem.get_numeric_value() for elem in numbers]
        
        # 分析两个数的零情况
        is_zero_a, non_zero_a, zero_count_a = self._analyze_zero_number(int(a)) if isinstance(a, int) else (False, int(a), 0)
        is_zero_b, non_zero_b, zero_count_b = self._analyze_zero_number(int(b)) if isinstance(b, int) else (False, int(b), 0)
        
        # 如果都不是整数或都没有末尾零，使用原数
        if not is_zero_a:
            non_zero_a, zero_count_a = a, 0
        if not is_zero_b:
            non_zero_b, zero_count_b = b, 0
        
        total_zero_count = zero_count_a + zero_count_b
        
        steps = []
        
        # 识别补零法
        zero_descriptions = []
        if zero_count_a > 0:
            zero_descriptions.append(f"{a}有{zero_count_a}个零")
        if zero_count_b > 0:
            zero_descriptions.append(f"{b}有{zero_count_b}个零")
        
        if zero_descriptions:
            steps.append(CalculationStep(
                description=f"{a} × {b} 使用补零法",
                operation="识别补零法",
                result=f"发现整零数：{', '.join(zero_descriptions)}"
            ))
        
        # 分解过程
        decomposition_parts = []
        if zero_count_a > 0:
            decomposition_parts.append(f"{a} = {non_zero_a} × 10^{zero_count_a}")
        else:
            decomposition_parts.append(f"{a} = {non_zero_a}")
            
        if zero_count_b > 0:
            decomposition_parts.append(f"{b} = {non_zero_b} × 10^{zero_count_b}")
        else:
            decomposition_parts.append(f"{b} = {non_zero_b}")
        
        steps.append(CalculationStep(
            description=f"分解：{'; '.join(decomposition_parts)}",
            operation="分解整零数",
            result=f"非零部分：{non_zero_a} × {non_zero_b}，总共补{total_zero_count}个零"
        ))
        
        # 计算非零部分乘法
        non_zero_result = non_zero_a * non_zero_b
        if non_zero_a != 1 and non_zero_b != 1:
            steps.append(CalculationStep(
                description=f"计算非零部分：{non_zero_a} × {non_zero_b} = {non_zero_result}",
                operation="非零部分乘法",
                result=non_zero_result
            ))
        elif non_zero_a == 1 or non_zero_b == 1:
            steps.append(CalculationStep(
                description=f"非零部分：{non_zero_a} × {non_zero_b} = {non_zero_result}",
                operation="简单乘法",
                result=non_zero_result
            ))
        
        # 补零操作
        if total_zero_count > 0:
            final_result = non_zero_result * (10 ** total_zero_count)
            if isinstance(non_zero_result, int):
                result_str = str(non_zero_result) + '0' * total_zero_count
            else:
                result_str = str(final_result)
            
            steps.append(CalculationStep(
                description=f"补零：{non_zero_result} 后面补{total_zero_count}个零 = {result_str}",
                operation="补零操作",
                result=result_str
            ))
        else:
            final_result = non_zero_result
        
        steps.append(CalculationStep(
            description=f"最终结果：{final_result}",
            operation="确认结果",
            result=final_result,
            formula="补零法：提取所有零，计算非零部分乘积，再补相应个数的零"
        ))
        
        return steps