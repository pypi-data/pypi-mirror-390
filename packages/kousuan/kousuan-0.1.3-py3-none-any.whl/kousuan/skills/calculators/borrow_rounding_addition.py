"""
借数凑整法加法实现
通过"借"和"还"的方式将数字调整为整数，简化计算
如98+67可以看作(100-2)+67=100+67-2=167-2=165
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class BorrowRoundingAddition(MathCalculator):
    """借数凑整法加法算法"""
    
    def __init__(self):
        super().__init__("借数凑整法", "通过借数凑整简化计算，先借后还", priority=4)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：其中一个数接近整十、整百等"""
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
            
            # 只处理正数且大于10
            if addend1 <= 10 or addend2 <= 10:
                return False
            
            ## 只处理两数总和大于50的情况
            if addend1 + addend2 <= 50:
                return False
            
            # 检查是否有数字接近整十、整百等（差距在1-9之间）
            def is_near_round(n):
                # 检查接近整百
                if n % 100 != 0 and n >= 50:
                    gap_to_hundred = 100 - (n % 100)

                    if 1 <= gap_to_hundred <= 20:
                        return True, gap_to_hundred, (n // 100 + 1) * 100
                    
                # 检查接近整十
                if n % 10 != 0:
                    gap_to_ten = 10 - (n % 10)
                    if 1 <= gap_to_ten <= 9:
                        return True, gap_to_ten, (n // 10 + 1) * 10
                
                return False, 0, n
            
            # 至少有一个数接近整数
            near1, gap1, round1 = is_near_round(addend1)
            near2, gap2, round2 = is_near_round(addend2)

            # 限制一下，两个数的gap相等时，刚好可以互补
            if (near1 or near2) and (gap1 + gap2) == 10:
                return True
            return False
        except Exception as e:
            print('借数凑整法加法算法异常', e)
            return False
    
    def _analyze_borrowing(self, addend1: int, addend2: int) -> tuple:
        """分析借数策略"""
        def get_borrowing_info(n):
            # 检查接近整百
            if n % 100 != 0 and n >= 50:
                gap_to_hundred = 100 - (n % 100)
                if 1 <= gap_to_hundred <= 20:  # 只考虑较小的借数
                    return True, gap_to_hundred, (n // 100 + 1) * 100, "整百"
                
            # 检查接近整十
            if n % 10 != 0:
                gap_to_ten = 10 - (n % 10)
                if 1 <= gap_to_ten <= 5:  # 只考虑较小的借数
                    return True, gap_to_ten, (n // 10 + 1) * 10, "整十"
            
            return False, 0, n, "无"
        
        # 分析两个数
        can_borrow1, gap1, round1, type1 = get_borrowing_info(addend1)
        can_borrow2, gap2, round2, type2 = get_borrowing_info(addend2)
        
        # 选择借数较少的数进行借数
        if can_borrow1 and can_borrow2:
            if gap1 >= gap2:
                return addend1, addend2, gap1, round1, type1, True
            else:
                return addend2, addend1, gap2, round2, type2, False
        elif can_borrow1:
            return addend1, addend2, gap1, round1, type1, True
        elif can_borrow2:
            return addend2, addend1, gap2, round2, type2, False
        else:
            return addend1, addend2, 0, addend1, "无", True
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建借数凑整法步骤"""
        numbers = formula.get_numbers()
        addend1 = int(numbers[0].get_numeric_value())
        addend2 = int(numbers[1].get_numeric_value())
        
        # 分析借数策略
        borrow_num, other_num, gap, round_num, round_type, first_is_borrow = self._analyze_borrowing(addend1, addend2)
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{addend1} + {addend2} 使用借数凑整法",
            operation="识别借数凑整法",
            result=f"{borrow_num} 接近{round_type} {round_num}，借 {gap} 凑整"
        ))
        
        steps.append(CalculationStep(
            description=f"借数凑整：{borrow_num} + {gap} = {round_num}",
            operation="借数凑整",
            result=f"将 {borrow_num} 看作 {round_num}"
        ))
        
        # 用整数计算
        temp_sum = round_num + other_num
        steps.append(CalculationStep(
            description=f"用整数计算：{round_num} + {other_num} = {temp_sum}",
            operation="整数计算",
            result=temp_sum
        ))
        
        # 还数
        final_result = temp_sum - gap
        steps.append(CalculationStep(
            description=f"还回借数：{temp_sum} - {gap} = {final_result}",
            operation="还数",
            result=final_result,
            formula=f"借数凑整法：借{gap}凑{round_type}，计算后还{gap}"
        ))
        
        return steps