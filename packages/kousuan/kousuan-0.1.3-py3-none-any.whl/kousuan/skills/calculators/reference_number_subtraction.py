"""
基准数法减法实现
找一个与两个数都接近的整十、整百数作为基准，计算它们与基准的差，再求差
适用于两个数都接近同一个基准数的情况
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ReferenceNumberSubtraction(MathCalculator):
    """基准数法减法算法"""
    
    def __init__(self):
        super().__init__("基准数法减法", "以基准数为参照计算差值，适用于两数都接近某个整数", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个数都接近同一个整十或整百数"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, (int, float)) and isinstance(subtrahend, (int, float))):
                return False
            
            # 转换为整数便于计算
            minuend, subtrahend = int(minuend), int(subtrahend)
            
            # 只处理正数且被减数大于减数
            if minuend <= subtrahend or minuend < 10 or subtrahend < 10:
                return False
            
            # 寻找合适的基准数
            reference = self._find_best_reference(minuend, subtrahend)
            return reference is not None
            
        except:
            return False
    
    def _find_best_reference(self, minuend: int, subtrahend: int):
        """找到最佳基准数"""
        # 候选基准数
        candidates = []
        
        # 计算数值范围
        min_val = min(minuend, subtrahend)
        max_val = max(minuend, subtrahend)
        
        # 添加整十数候选
        for i in range(max(1, min_val // 10), (max_val // 10) + 2):
            candidate = i * 10
            dist1 = abs(minuend - candidate)
            dist2 = abs(subtrahend - candidate)
            max_dist = max(dist1, dist2)
            if max_dist <= 10:  # 最大距离不超过10
                candidates.append((candidate, max_dist, "十"))
        
        # 添加整百数候选
        if max_val >= 50:
            for i in range(max(1, min_val // 100), (max_val // 100) + 2):
                candidate = i * 100
                dist1 = abs(minuend - candidate)
                dist2 = abs(subtrahend - candidate)
                max_dist = max(dist1, dist2)
                if max_dist <= 20:  # 整百数允许更大的距离
                    candidates.append((candidate, max_dist, "百"))
        
        if not candidates:
            return None
        
        # 选择距离最小的基准数
        best = min(candidates, key=lambda x: x[1])
        return best[0], best[2]
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建基准数法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        # 寻找最佳基准数
        result = self._find_best_reference(minuend, subtrahend)
        if result is None:
            raise ValueError("No suitable reference found")
        
        reference, unit_type = result
        
        # 计算与基准数的差值
        minuend_diff = minuend - reference
        subtrahend_diff = subtrahend - reference
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用基准数法",
            operation="识别基准数法",
            result=f"选择整{unit_type}数 {reference} 作为基准数"
        ))
        
        steps.append(CalculationStep(
            description=f"计算与基准数的差值",
            operation="计算差值",
            result=f"{minuend} 比 {reference} {'多' if minuend_diff >= 0 else '少'} {abs(minuend_diff)}；{subtrahend} 比 {reference} {'多' if subtrahend_diff >= 0 else '少'} {abs(subtrahend_diff)}"
        ))
        
        # 用基准数表示原数
        steps.append(CalculationStep(
            description=f"用基准数表示：{minuend} = {reference} + ({minuend_diff:+})，{subtrahend} = {reference} + ({subtrahend_diff:+})",
            operation="基准数表示",
            result=f"转换为基准数形式"
        ))
        
        # 应用减法性质
        steps.append(CalculationStep(
            description=f"应用减法性质：[{reference} + ({minuend_diff:+})] - [{reference} + ({subtrahend_diff:+})] = ({minuend_diff:+}) - ({subtrahend_diff:+})",
            operation="减法性质",
            result="基准数相互抵消"
        ))
        
        # 计算最终结果
        final_result = minuend_diff - subtrahend_diff
        steps.append(CalculationStep(
            description=f"计算差值的差：({minuend_diff:+}) - ({subtrahend_diff:+}) = {final_result}",
            operation="计算结果",
            result=final_result,
            formula=f"基准数法：(a+x) - (a+y) = x - y，其中a={reference}"
        ))
        
        return steps