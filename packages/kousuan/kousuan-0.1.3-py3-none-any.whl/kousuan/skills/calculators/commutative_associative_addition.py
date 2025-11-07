"""
交换结合法加法实现
利用加法的交换律和结合律重新排列加数，使计算更简单
适用于能够重新组合得到更简单计算的情况
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class CommutativeAssociativeAddition(MathCalculator):
    """交换结合法加法算法"""
    
    def __init__(self):
        super().__init__("交换结合法", "利用交换律和结合律重新排列，优化计算", priority=1)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：适用于能通过重新排列简化的加法"""
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
            
            # 这是一个兜底算法，优先级最低
            # 主要用于演示交换律和结合律的概念
            # 只在其他更具体的算法都不适用时才使用
            
            # 检查是否有重新排列的价值
            # 例如：个位数字的重新组合能产生进位或简化
            
            # 简单示例：如果两个数都是两位数，检查是否可以通过交换获得更好的计算顺序
            if 10 <= addend1 <= 99 and 10 <= addend2 <= 99:
                # 获取各位数字
                a_tens, a_ones = addend1 // 10, addend1 % 10
                b_tens, b_ones = addend2 // 10, addend2 % 10
                
                # 如果重新组合后能得到更简单的计算，则适用
                # 例如：23 + 45 可以看作 (20+40) + (3+5) = 60 + 8 = 68
                # 但这种情况通常会被其他算法（如由高到低位法）覆盖
                
                # 这里我们只在非常特殊的情况下应用，作为演示用途
                return False  # 暂时禁用，避免与其他算法冲突
            
            return False
        except:
            return False
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建交换结合法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用交换结合法",
            operation="识别交换结合法",
            result="利用交换律和结合律重新排列"
        ))
        
        # 演示交换律
        steps.append(CalculationStep(
            description=f"交换律：{addend1} + {addend2} = {addend2} + {addend1}",
            operation="应用交换律",
            result=f"可以交换加数顺序"
        ))
        
        # 如果是两位数，演示分解和重新组合
        if 10 <= addend1 <= 99 and 10 <= addend2 <= 99:
            a_tens, a_ones = addend1 // 10, addend1 % 10
            b_tens, b_ones = addend2 // 10, addend2 % 10
            
            steps.append(CalculationStep(
                description=f"分解：{addend1} = {a_tens * 10} + {a_ones}，{addend2} = {b_tens * 10} + {b_ones}",
                operation="数字分解",
                result=f"按位分解后重新组合"
            ))
            
            steps.append(CalculationStep(
                description=f"结合律重组：({a_tens * 10} + {b_tens * 10}) + ({a_ones} + {b_ones})",
                operation="应用结合律",
                result=f"同类项结合"
            ))
            
            tens_sum = (a_tens + b_tens) * 10
            ones_sum = a_ones + b_ones
            
            steps.append(CalculationStep(
                description=f"分别计算：{a_tens * 10} + {b_tens * 10} = {tens_sum}，{a_ones} + {b_ones} = {ones_sum}",
                operation="分组计算",
                result=f"十位和：{tens_sum}，个位和：{ones_sum}"
            ))
            
            final_result = tens_sum + ones_sum
            steps.append(CalculationStep(
                description=f"合并结果：{tens_sum} + {ones_sum} = {final_result}",
                operation="合并结果",
                result=final_result,
                formula="交换结合法：(a+c)+(b+d) = (a+b)+(c+d)"
            ))
        else:
            # 简单情况直接计算
            final_result = addend1 + addend2
            steps.append(CalculationStep(
                description=f"直接计算：{addend1} + {addend2} = {final_result}",
                operation="直接相加",
                result=final_result,
                formula="交换结合法：a + b = b + a"
            ))
        
        return steps