"""
同加同减法实现
将被减数和减数同时加上或减去同一个数，使减数变为整十、整百，简化计算
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class SameAddSameSubtract(MathCalculator):
    """同加同减法算法"""
    
    def __init__(self):
        super().__init__("同加同减法", "同时调整被减数和减数，简化减法计算", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：减数接近整十、整百，且调整后计算更方便"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            minuend, subtrahend = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(minuend, (int, float)) and isinstance(subtrahend, (int, float))):
                return False
            
            # 转换为整数
            minuend, subtrahend = int(minuend), int(subtrahend)
            
            # 只处理正数且被减数大于减数
            if minuend <= subtrahend or minuend < 10 or subtrahend < 10:
                return False
            
            # 检查是否有合适的调整方案
            return self._find_best_adjustment(minuend, subtrahend) is not None
            
        except:
            return False
    
    def _find_best_adjustment(self, minuend: int, subtrahend: int):
        """寻找最佳调整方案"""
        candidates = []
        
        # 调整到最近的整十数
        nearest_ten = round(subtrahend / 10) * 10
        if nearest_ten != subtrahend:
            adjustment = nearest_ten - subtrahend
            if abs(adjustment) <= 5:  # 调整幅度不超过5
                new_minuend = minuend + adjustment
                # 检查调整后是否更容易计算
                if new_minuend > 0 and self._is_easier_calculation(new_minuend, nearest_ten):
                    candidates.append((nearest_ten, adjustment, "十"))
        
        # 调整到最近的整百数（如果数字较大）
        if subtrahend >= 50:
            nearest_hundred = round(subtrahend / 100) * 100
            if nearest_hundred != subtrahend:
                adjustment = nearest_hundred - subtrahend
                if abs(adjustment) <= 10:  # 整百数允许更大的调整幅度
                    new_minuend = minuend + adjustment
                    if new_minuend > 0 and self._is_easier_calculation(new_minuend, nearest_hundred):
                        candidates.append((nearest_hundred, adjustment, "百"))
        
        if not candidates:
            return None
        
        # 选择调整幅度最小的方案
        best = min(candidates, key=lambda x: abs(x[1]))
        return best
    
    def _is_easier_calculation(self, new_minuend: int, round_subtrahend: int) -> bool:
        """判断调整后的计算是否更容易"""
        # 整十数、整百数的减法通常更容易
        if round_subtrahend % 10 == 0:
            return True
        if round_subtrahend % 100 == 0:
            return True
        return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建同加同减法步骤"""
        numbers = formula.get_numbers()
        minuend = int(numbers[0].get_numeric_value())
        subtrahend = int(numbers[1].get_numeric_value())
        
        # 找到最佳调整方案
        result = self._find_best_adjustment(minuend, subtrahend)
        if result is None:
            raise ValueError("No suitable adjustment found")
        
        target_subtrahend, adjustment, unit_type = result
        new_minuend = minuend + adjustment
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用同加同减法",
            operation="识别同加同减法",
            result=f"将减数调整为整{unit_type}数 {target_subtrahend}"
        ))
        
        if adjustment > 0:
            steps.append(CalculationStep(
                description=f"同时加 {adjustment}：({minuend} + {adjustment}) - ({subtrahend} + {adjustment}) = {new_minuend} - {target_subtrahend}",
                operation="同时增加",
                result=f"转换为 {new_minuend} - {target_subtrahend}"
            ))
        else:
            steps.append(CalculationStep(
                description=f"同时减 {abs(adjustment)}：({minuend} - {abs(adjustment)}) - ({subtrahend} - {abs(adjustment)}) = {new_minuend} - {target_subtrahend}",
                operation="同时减少",
                result=f"转换为 {new_minuend} - {target_subtrahend}"
            ))
        
        steps.append(CalculationStep(
            description=f"计算简化后的减法：{new_minuend} - {target_subtrahend}",
            operation="简化计算",
            result="整十数减法更容易计算"
        ))
        
        # 计算最终结果
        final_result = new_minuend - target_subtrahend
        steps.append(CalculationStep(
            description=f"{new_minuend} - {target_subtrahend} = {final_result}",
            operation="计算结果",
            result=final_result,
            formula="同加同减法：(a±k) - (b±k) = a - b"
        ))
        
        return steps