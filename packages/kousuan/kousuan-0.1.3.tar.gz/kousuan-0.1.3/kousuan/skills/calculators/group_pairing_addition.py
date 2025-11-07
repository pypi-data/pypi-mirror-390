"""
分组配对法加法实现
在多个数的加法中寻找能够配对的数字，优先计算配对组合
适用于多个数相加的情况，如12+18+25+75，可以配对为(12+18)+(25+75)=30+100=130
注意：这个算子主要用于演示，实际多数加法会由混合运算优化器处理
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class GroupPairingAddition(MathCalculator):
    """分组配对法加法算法"""
    
    def __init__(self):
        super().__init__("分组配对法", "多数加法中寻找配对组合，优化计算顺序", priority=2)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：暂时只处理两个数的加法，但寻找配对特征"""
        if formula.type != "addition":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            addend1, addend2 = [elem.get_numeric_value() for elem in numbers]
            if not (isinstance(addend1, (int, float)) and isinstance(addend2, (int, float))):
                return False
            
            # 转换为整数
            addend1, addend2 = int(addend1), int(addend2)
            
            # 只处理正数
            if addend1 <= 0 or addend2 <= 0:
                return False
            
            # 寻找配对特征：
            # 1. 两数的某些位数能配对成整十、整百
            # 2. 两数都是特定倍数（如5的倍数）
            # 3. 两数结构相似但不完全相同
            
            # 检查是否都是5的倍数
            if addend1 % 5 == 0 and addend2 % 5 == 0 and addend1 != addend2:
                return True
            
            # 检查是否都是25的倍数
            if addend1 % 25 == 0 and addend2 % 25 == 0 and addend1 != addend2:
                return True
            
            # 检查个位数是否能配对
            ones1, ones2 = addend1 % 10, addend2 % 10
            if ones1 + ones2 == 10 and addend1 >= 20 and addend2 >= 20:
                # 但要排除其他高优先级算法已经覆盖的情况
                tens1, tens2 = addend1 // 10, addend2 // 10
                # 如果十位相同，会被同头数加法覆盖
                if tens1 == tens2:
                    return False
                return True
            
            return False
        except:
            return False
    
    def _find_pairing_strategy(self, addend1: int, addend2: int) -> tuple:
        """找到配对策略"""
        ones1, ones2 = addend1 % 10, addend2 % 10
        tens1, tens2 = addend1 // 10, addend2 // 10
        
        # 个位配对策略
        if ones1 + ones2 == 10:
            return ("个位配对", ones1, ones2, tens1 * 10, tens2 * 10)
        
        # 倍数配对策略
        if addend1 % 25 == 0 and addend2 % 25 == 0:
            return ("25倍数配对", addend1 // 25, addend2 // 25, 25, 25)
        
        if addend1 % 5 == 0 and addend2 % 5 == 0:
            return ("5倍数配对", addend1 // 5, addend2 // 5, 5, 5)
        
        return ("直接相加", addend1, addend2, 1, 1)
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建分组配对法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用分组配对法",
            operation="识别配对法",
            result="寻找数字间的配对关系"
        ))
        
        # 分析配对策略
        strategy, val1, val2, base1, base2 = self._find_pairing_strategy(addend1, addend2)
        
        if strategy == "个位配对":
            steps.append(CalculationStep(
                description=f"发现个位配对：{val1} + {val2} = 10",
                operation="个位配对识别",
                result=f"个位数 {val1} 和 {val2} 能凑成10"
            ))
            
            steps.append(CalculationStep(
                description=f"分离十位部分：{base1} 和 {base2}",
                operation="十位分离",
                result=f"十位部分分别为 {base1} 和 {base2}"
            ))
            
            tens_sum = base1 + base2
            steps.append(CalculationStep(
                description=f"计算十位和：{base1} + {base2} = {tens_sum}",
                operation="十位相加",
                result=tens_sum
            ))
            
            final_result = tens_sum + 10
            steps.append(CalculationStep(
                description=f"加上个位配对结果：{tens_sum} + 10 = {final_result}",
                operation="合并结果",
                result=final_result,
                formula="分组配对法：个位配对 + 十位相加"
            ))
        
        elif strategy == "25倍数配对":
            steps.append(CalculationStep(
                description=f"发现25倍数配对：{addend1} = {val1}×25，{addend2} = {val2}×25",
                operation="25倍数配对识别",
                result=f"两数都是25的倍数"
            ))
            
            multiplier_sum = val1 + val2
            steps.append(CalculationStep(
                description=f"先算倍数和：{val1} + {val2} = {multiplier_sum}",
                operation="倍数相加",
                result=multiplier_sum
            ))
            
            final_result = multiplier_sum * 25
            steps.append(CalculationStep(
                description=f"乘以基数：{multiplier_sum} × 25 = {final_result}",
                operation="配对计算",
                result=final_result,
                formula="分组配对法：25倍数配对"
            ))
        
        elif strategy == "5倍数配对":
            steps.append(CalculationStep(
                description=f"发现5倍数配对：{addend1} = {val1}×5，{addend2} = {val2}×5",
                operation="5倍数配对识别",
                result=f"两数都是5的倍数"
            ))
            
            multiplier_sum = val1 + val2
            steps.append(CalculationStep(
                description=f"先算倍数和：{val1} + {val2} = {multiplier_sum}",
                operation="倍数相加",
                result=multiplier_sum
            ))
            
            final_result = multiplier_sum * 5
            steps.append(CalculationStep(
                description=f"乘以基数：{multiplier_sum} × 5 = {final_result}",
                operation="配对计算",
                result=final_result,
                formula="分组配对法：5倍数配对"
            ))
        
        else:
            final_result = addend1 + addend2
            steps.append(CalculationStep(
                description=f"直接相加：{addend1} + {addend2} = {final_result}",
                operation="直接计算",
                result=final_result,
                formula="分组配对法：未找到特殊配对"
            ))
        
        return steps