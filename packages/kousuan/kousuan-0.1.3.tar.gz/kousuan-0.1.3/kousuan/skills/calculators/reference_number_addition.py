"""
基准数法加法实现
选择一个接近两个加数的基准数，计算各自与基准数的差值，然后合并计算
适用于两个数都接近某个整数的情况，如78+87（基准80）
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ReferenceNumberAddition(MathCalculator):
    """基准数法加法算法"""
    
    def __init__(self):
        super().__init__("基准数法", "选择基准数计算差值，适用于两数都接近某个整数的加法", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个数都接近同一个整十数"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, (int, float)) and isinstance(addend2, (int, float))):
                return False
            
            # 转换为整数便于计算
            addend1, addend2 = int(addend1), int(addend2)
            
            # 只处理正数且大于10的情况
            if addend1 <= 10 or addend2 <= 10:
                return False
            
            # 寻找合适的基准数（取平均值然后向上或向下取整到最近的十位）
            avg = (addend1 + addend2) / 2
            reference_candidates = []
            
            # 尝试最近的整十数作为基准
            lower_ten = int(avg // 10) * 10
            upper_ten = lower_ten + 10
            
            reference_candidates.extend([lower_ten, upper_ten])
            
            # 尝试整百数作为基准（如果数字较大）
            if avg >= 50:
                lower_hundred = int(avg // 100) * 100
                upper_hundred = lower_hundred + 100
                reference_candidates.extend([lower_hundred, upper_hundred])
            
            # 检查是否有合适的基准数（两个数与基准数的距离都不超过基准数的20%）
            for ref in reference_candidates:
                if ref > 0:
                    dist1 = abs(addend1 - ref)
                    dist2 = abs(addend2 - ref)
                    max_dist = max(ref * 0.2, 10)  # 至少允许10的距离
                    if dist1 <= max_dist and dist2 <= max_dist:
                        return True
            
            return False
        except:
            return False
    
    def _find_best_reference(self, addend1: int, addend2: int) -> int:
        """找到最佳基准数"""
        avg = (addend1 + addend2) / 2
        
        # 候选基准数
        candidates = []
        
        # 整十数
        lower_ten = int(avg // 10) * 10
        upper_ten = lower_ten + 10
        candidates.extend([lower_ten, upper_ten])
        
        # 整百数（如果数字较大）
        if avg >= 50:
            lower_hundred = int(avg // 100) * 100
            if lower_hundred > 0:
                candidates.append(lower_hundred)
            upper_hundred = lower_hundred + 100
            candidates.append(upper_hundred)
        
        # 选择使两个数的距离平方和最小的基准数
        best_ref = candidates[0]
        min_score = float('inf')
        
        for ref in candidates:
            if ref > 0:
                score = (addend1 - ref) ** 2 + (addend2 - ref) ** 2
                if score < min_score:
                    min_score = score
                    best_ref = ref
        
        return best_ref
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建基准数法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        # 寻找最佳基准数
        reference = self._find_best_reference(addend1, addend2)
        
        # 计算与基准数的差值
        diff1 = addend1 - reference
        diff2 = addend2 - reference
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用基准数法",
            operation="识别基准数法",
            result=f"选择 {reference} 作为基准数"
        ))
        
        steps.append(CalculationStep(
            description=f"计算与基准数的差值",
            operation="计算差值",
            result=f"{addend1} 比 {reference} {'多' if diff1 >= 0 else '少'} {abs(diff1)}；{addend2} 比 {reference} {'多' if diff2 >= 0 else '少'} {abs(diff2)}"
        ))
        
        # 计算两个基准数的和
        base_sum = reference * 2
        steps.append(CalculationStep(
            description=f"计算基准和：{reference} + {reference} = {base_sum}",
            operation="基准和计算",
            result=base_sum
        ))
        
        # 合并差值
        total_diff = diff1 + diff2
        steps.append(CalculationStep(
            description=f"合并差值：{diff1:+} + {diff2:+} = {total_diff:+}",
            operation="差值合并",
            result=total_diff
        ))
        
        # 计算最终结果
        final_result = base_sum + total_diff
        steps.append(CalculationStep(
            description=f"最终结果：{base_sum} + ({total_diff:+}) = {final_result}",
            operation="合并结果",
            result=final_result,
            formula=f"基准数法：(a-r) + (b-r) + 2r = a + b，其中r={reference}"
        ))
        
        return steps