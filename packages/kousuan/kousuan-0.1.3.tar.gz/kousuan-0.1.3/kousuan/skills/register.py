"""
智能计算器引擎注册器
"""

from typing import List, Dict, Any, Optional
from .base_types import Formula, MathCalculator
from .formula_parser import FormulaParser


class SmartCalculatorReister:
    """智能计算器引擎 - 算法自动匹配机制"""
    
    def __init__(self):
        self.calculators: List[MathCalculator] = []
        self._register_default_calculators()
    
    def _register_default_calculators(self):
        """注册默认的算子"""
        # 导入具体的算子实现
        from .calculators.same_head_sum_ten_multiplication import SameHeadSumTenMultiplication
        from .calculators.head_sum_ten_tail_same_multiplication import HeadSumTenTailSameMultiplication
        from .calculators.ten_complement_addition import TenComplementAddition
        from .calculators.break_ten_subtraction import BreakTenSubtraction
        from .calculators.complement_addition_subtraction import ComplementAdditionSubtraction
        from .calculators.reversed_number_subtraction import ReversedNumberSubtraction
        from .calculators.multiply_by_nine import MultiplyByNine
        from .calculators.divide_by_five import DivideByFive
        from .calculators.multiply_by_eleven import MultiplyByEleven
        from .calculators.near_hundred_multiplication import NearHundredMultiplication
        from .calculators.near_hundreds_multiplication import NearHundredsMultiplication
        from .calculators.two_digit_square import TwoDigitSquare
        
        # 新增的算法
        from .calculators.multiply_by_twenty_five import MultiplyByTwentyFive
        from .calculators.divide_by_twenty_five import DivideByTwentyFive
        from .calculators.tens_one_multiplication import TensOneMultiplication
        from .calculators.reversed_number_addition import ReversedNumberAddition
        from .calculators.complement_ten_multiply_repeated import ComplementTenMultiplyRepeated
        from .calculators.hundred_plus_some_multiplication import HundredPlusSomeMultiplication
        from .calculators.hundred_plus_few_multiplication import HundredPlusFewMultiplication
        from .calculators.middle_number_multiplication import MiddleNumberMultiplication
        from .calculators.two_digit_subtraction import TwoDigitSubtraction
        
        # 通用乘法算法（最低优先级）
        from .calculators.general_multiplication import GeneralMultiplication
        
        # 新增的减法算法
        from .calculators.same_number_subtraction import SameNumberSubtraction
        from .calculators.consecutive_number_subtraction import ConsecutiveNumberSubtraction
        from .calculators.same_head_subtraction import SameHeadSubtraction
        from .calculators.tail_complement_ten_subtraction import TailComplementTenSubtraction
        from .calculators.near_hundred_subtraction import NearHundredSubtraction
        
        # 最新添加的减法算法
        from .calculators.split_subtraction import SplitSubtraction
        from .calculators.high_to_low_digit_subtraction import HighToLowDigitSubtraction
        from .calculators.reference_number_subtraction import ReferenceNumberSubtraction
        from .calculators.same_add_same_subtract import SameAddSameSubtract
        from .calculators.power_of_ten_subtraction import PowerOfTenSubtraction
        from .calculators.chain_subtraction_to_addition import ChainSubtractionToAddition
        from .calculators.remove_zero_subtraction import RemoveZeroSubtraction
        from .calculators.inverse_addition_subtraction import InverseAdditionSubtraction
        
        # 新增的加法算法
        from .calculators.same_number_addition import SameNumberAddition
        from .calculators.consecutive_number_addition import ConsecutiveNumberAddition
        from .calculators.same_head_addition import SameHeadAddition
        from .calculators.near_hundred_addition import NearHundredAddition
        from .calculators.reference_number_addition import ReferenceNumberAddition
        from .calculators.high_to_low_digit_addition import HighToLowDigitAddition
        from .calculators.segment_sum_addition import SegmentSumAddition
        from .calculators.rounding_addition import RoundingAddition
        from .calculators.split_addition import SplitAddition
        from .calculators.group_pairing_addition import GroupPairingAddition
        from .calculators.borrow_rounding_addition import BorrowRoundingAddition
        from .calculators.commutative_associative_addition import CommutativeAssociativeAddition
        
        # 新增的乘法算法
        from .calculators.multiply_by_powers_of_ten import MultiplyByPowersOfTen
        from .calculators.multiply_by_one_hundred_twenty_five import MultiplyByOneHundredTwentyFive
        from .calculators.multiply_by_twelve import MultiplyByTwelve
        from .calculators.multiply_by_fifteen import MultiplyByFifteen
        from .calculators.multiply_by_nineteen import MultiplyByNineteen
        from .calculators.difference_method_multiplication import DifferenceMethodMultiplication
        from .calculators.split_method_multiplication import SplitMethodMultiplication
        from .calculators.commutative_associative_multiplication import CommutativeAssociativeMultiplication
        
        # 新增的除法算法（按优先级重新排序）
        from .calculators.multiplication_table_division import MultiplicationTableDivision  # priority=7
        from .calculators.round_number_division import RoundNumberDivision  # priority=6
        from .calculators.near_round_division import NearRoundDivision  # priority=5
        from .calculators.split_division import SplitDivision  # priority=4
        from .calculators.integer_multiple_division import IntegerMultipleDivision  # priority=3
        from .calculators.general_division import GeneralDivision  # priority=1
        from .calculators.multiply_by_five import MultiplyByFive  # priority=4
        
        # 最新添加的除法算法
        from .calculators.power_of_ten_division import PowerOfTenDivision  # priority=8
        from .calculators.halving_division import HalvingDivision  # priority=7
        from .calculators.consecutive_halving_division import ConsecutiveHalvingDivision  # priority=7
        from .calculators.divide_by_one_hundred_twenty_five import DivideByOneHundredTwentyFive  # priority=6
        from .calculators.quotient_invariant_division import QuotientInvariantDivision  # priority=5
        from .calculators.reduction_division import ReductionDivision  # priority=6
        from .calculators.divide_by_nine import DivideByNine  # priority=6
        from .calculators.divide_by_eleven import DivideByEleven  # priority=6
        from .calculators.split_divisor_division import SplitDivisorDivision  # priority=5
        from .calculators.first_digit_estimate_division import FirstDigitEstimateDivision  # priority=4
        
        self.calculators = [
            MultiplyByPowersOfTen(),  # 优先级5：补零法（支持所有整零数）
            MultiplyByFive(),
            MultiplyByNine(),
            MultiplyByTwentyFive(),
            MultiplyByOneHundredTwentyFive(),  # 优先级3：乘125
            MultiplyByTwelve(),  # 优先级3：乘12
            MultiplyByFifteen(),  # 优先级3：乘15
            MultiplyByNineteen(),  # 优先级3：乘19
            DivideByFive(),  # 暂时禁用，解析器问题
            DivideByTwentyFive(),
            MultiplyByEleven(),
            TenComplementAddition(),
            SameNumberAddition(),
            ConsecutiveNumberAddition(), 
            RoundingAddition(),
            SameHeadAddition(),
            BorrowRoundingAddition(),
            ReferenceNumberAddition(),
            SegmentSumAddition(),
            HighToLowDigitAddition(),
            SplitAddition(),
            NearHundredAddition(),
            GroupPairingAddition(),
            CommutativeAssociativeAddition(),
            BreakTenSubtraction(),
            TwoDigitSubtraction(),
            SameNumberSubtraction(),
            ConsecutiveNumberSubtraction(),
            SameHeadSubtraction(),
            TailComplementTenSubtraction(),
            NearHundredSubtraction(),
            ComplementAdditionSubtraction(),
            ReversedNumberSubtraction(),
            # 最新添加的减法算法
            SplitSubtraction(),
            HighToLowDigitSubtraction(),
            ReferenceNumberSubtraction(),
            SameAddSameSubtract(),
            PowerOfTenSubtraction(),
            ChainSubtractionToAddition(),
            RemoveZeroSubtraction(),
            InverseAdditionSubtraction(),
            ReversedNumberAddition(),
            TensOneMultiplication(),
            ComplementTenMultiplyRepeated(),
            SameHeadSumTenMultiplication(),
            HeadSumTenTailSameMultiplication(),
            NearHundredsMultiplication(),  # 更通用的整百数乘法，优先级更高
            NearHundredMultiplication(),
            HundredPlusSomeMultiplication(),
            HundredPlusFewMultiplication(),  # 几百零几乘法
            MiddleNumberMultiplication(),
            TwoDigitSquare(),
            DifferenceMethodMultiplication(),  # 优先级6：差额法
            CommutativeAssociativeMultiplication(),  # 优先级5：交换结合法
            SplitMethodMultiplication(),  # 优先级4：分拆法
            GeneralMultiplication(),  # 通用乘法算法，最低优先级
            # 除法算法（按优先级排序：8→7→6→5→4→3→1）
            PowerOfTenDivision(),          # 优先级8：补零法除法
            MultiplicationTableDivision(), # 优先级7：九九表速算
            HalvingDivision(),             # 优先级7：减半法
            ConsecutiveHalvingDivision(),  # 优先级7：连续减半法
            RoundNumberDivision(),          # 优先级6：整十除法
            DivideByOneHundredTwentyFive(), # 优先级6：除以125
            ReductionDivision(),           # 优先级6：约分法
            DivideByNine(),                # 优先级6：除以9
            DivideByEleven(),              # 优先级6：除以11
            NearRoundDivision(),           # 优先级5：近整十除法
            QuotientInvariantDivision(),   # 优先级5：商不变性质
            SplitDivisorDivision(),        # 优先级5：拆分除数法
            SplitDivision(),               # 优先级4：拆分除法
            FirstDigitEstimateDivision(),  # 优先级4：首数估商法
            IntegerMultipleDivision(),      # 优先级3：整数倍数除法
            GeneralDivision(),             # 优先级1：通用除法（兜底）
        ]
    
    def get_division_remainder(self):
        from .calculators.division_with_remainder import DivisionWithRemainder  # priority=4
        """设置除法计算模式"""
        return DivisionWithRemainder()
    def get_revert_calculator(self) -> MathCalculator:
        """获取逆运算算子实例"""
        from .calculators.revert_calculator import RevertCalculator
        return RevertCalculator()
    def register_calculator(self, calculator: MathCalculator):
        """注册新的算子"""
        self.calculators.append(calculator)
    
    def find_matching_calculators(self, formula: Formula) -> List[MathCalculator]:
        """找到所有匹配的算子候选集合"""
        matching = []
        for calc in self.calculators:
            if calc.is_match_pattern(formula):
                matching.append(calc)
        return matching
