"""
凑整法加法实现
将数字凑成整十、整百、整千等，简化心算过程
适用于接近整数倍的加法运算，如27+73=100、48+52=100
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class RoundingAddition(MathCalculator):
    """凑整法加法算法"""
    
    def __init__(self):
        super().__init__("凑整法", "将数字凑成整十、整百、整千等，简化心算", priority=8)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：两个数能凑成整十、整百、整千等"""
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
            
            sum_result = addend1 + addend2
            
            # 检查是否能凑成整十、整百、整千等
            round_targets = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 
                           200, 300, 400, 500, 600, 700, 800, 900, 1000]
            
            return sum_result in round_targets
        except:
            return False
    
    def _get_round_type(self, result: int) -> str:
        """获取凑整类型"""
        if result == 10:
            return "凑十"
        elif result < 100 and result % 10 == 0:
            return f"凑{result}"
        elif result == 100:
            return "凑百"
        elif result < 1000 and result % 100 == 0:
            return f"凑{result//100}百"
        elif result == 1000:
            return "凑千"
        else:
            return f"凑{result}"
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建凑整法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        result = addend1 + addend2
        round_type = self._get_round_type(result)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用凑整法",
            operation="识别凑整法",
            result=f"两数相加能{round_type}"
        ))
        
        steps.append(CalculationStep(
            description=f"观察两数特征",
            operation="数字分析",
            result=f"{addend1} 和 {addend2} 互为补数，相加恰好等于 {result}"
        ))
        
        # 展示凑整过程
        if result <= 100:
            # 展示个位和十位的凑整
            ones1 = addend1 % 10
            ones2 = addend2 % 10
            tens1 = addend1 // 10
            tens2 = addend2 // 10
            
            if ones1 + ones2 == 10:
                steps.append(CalculationStep(
                    description=f"个位凑十：{ones1} + {ones2} = 10",
                    operation="个位凑十",
                    result="个位凑成10"
                ))
                
                if tens1 + tens2 > 0:
                    steps.append(CalculationStep(
                        description=f"十位相加：{tens1} + {tens2} = {tens1 + tens2}",
                        operation="十位相加",
                        result=f"十位部分为 {(tens1 + tens2) * 10}"
                    ))
            
        steps.append(CalculationStep(
            description=f"直接得出结果：{addend1} + {addend2} = {result}",
            operation="凑整计算",
            result=result,
            formula=f"凑整法：两数互补凑成整数"
        ))
        
        return steps