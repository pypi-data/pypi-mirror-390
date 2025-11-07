"""
求分数倒数等式算子 - 处理 #frac{@}{@}#×#frac{58}{9}#=1 类型题目
"""

from typing import Dict, Any
from fractions import Fraction
from ..base_types import FractionCalculator, FractionProblem, FractionResult, FractionStep, OperationType


class ReciprocalEquationCalculator(FractionCalculator):
    """求分数倒数等式算子"""
    
    def __init__(self):
        super().__init__("求倒数等式", "根据乘积为1求未知分数", priority=9)
    
    def is_match_pattern(self, problem: FractionProblem) -> Dict[str, Any]:
        """匹配求倒数等式问题"""
        # 匹配 a × b = 1 类型，其中一个是未知数
        if (problem.operation == OperationType.MULTIPLY and 
            len(problem.operands) == 1 and 
            problem.target_format in ("reciprocal", 'fraction')):
            return {"matched": True, "score": 1.0, "reason": "求倒数等式"}
        
        # 匹配 1 ÷ a = ? 类型
        if (problem.operation == OperationType.DIVIDE and 
            len(problem.operands) >= 2 and
            problem.operands[0].fraction == Fraction(1)):
            return {"matched": True, "score": 1.0, "reason": "1除以分数求倒数"}
        
        return {"matched": False, "score": 0.0, "reason": "不是求倒数等式"}
    
    def solve(self, problem: FractionProblem) -> FractionResult:
        """执行求倒数等式计算"""
        try:
            steps = []
            
            if problem.operation == OperationType.MULTIPLY:
                # 处理 ? × a = 1 类型
                known_fraction = problem.operands[0].fraction
                
                steps.append(FractionStep(
                    description=f"根据倒数定义：两个数相乘等于1，则互为倒数",
                    operation="倒数定义",
                    result="需要找到与已知分数相乘等于1的分数"
                ))
                
                steps.append(FractionStep(
                    description=f"已知分数：{known_fraction}",
                    operation="确定已知条件",
                    result=str(known_fraction)
                ))
                
                # 求倒数：交换分子分母
                reciprocal = Fraction(known_fraction.denominator, known_fraction.numerator)
                
                steps.append(FractionStep(
                    description=f"分数倒数技巧：分子分母互换位置",
                    operation="交换分子分母",
                    result=f"{known_fraction} → {reciprocal}",
                    formula="分数的倒数 = 分母/分子"
                ))
                
                # 验证
                steps.append(FractionStep(
                    description=f"验证：{reciprocal} × {known_fraction} = {reciprocal * known_fraction}",
                    operation="验证倒数",
                    result="乘积为1，验证正确",
                    formula=f"{reciprocal} × {known_fraction} = 1"
                ))
                
                return FractionResult(
                    success=True,
                    result=reciprocal,
                    steps=steps,
                    step_count=len(steps),
                    formula=f"求{known_fraction}的倒数 = {reciprocal}",
                    validation=True
                )
                
            elif problem.operation == OperationType.DIVIDE:
                # 处理 1 ÷ a = ? 类型
                dividend = problem.operands[0].fraction  # 1
                divisor = problem.operands[1].fraction   # 要求倒数的分数
                
                steps.append(FractionStep(
                    description=f"1除以一个数的结果就是这个数的倒数",
                    operation="倒数定义",
                    result="1 ÷ 分数 = 分数的倒数"
                ))
                
                steps.append(FractionStep(
                    description=f"要求：1 ÷ {divisor}",
                    operation="确定问题",
                    result=f"求{divisor}的倒数"
                ))
                
                # 交换分子分母求倒数
                reciprocal = Fraction(divisor.denominator, divisor.numerator)
                
                steps.append(FractionStep(
                    description=f"分数倒数：交换分子分母",
                    operation="求倒数",
                    result=f"{divisor} → {reciprocal}",
                    formula="分数的倒数 = 分母/分子"
                ))
                
                # 验证
                steps.append(FractionStep(
                    description=f"验证：1 ÷ {divisor} = {reciprocal}",
                    operation="验证计算",
                    result=str(reciprocal),
                    formula=f"1 ÷ {divisor} = {reciprocal}"
                ))
                
                return FractionResult(
                    success=True,
                    result=reciprocal,
                    steps=steps,
                    step_count=len(steps),
                    formula=f"1 ÷ {divisor} = {reciprocal}",
                    validation=True
                )
            
        except Exception as e:
            return FractionResult(
                success=False,
                error=f"求倒数等式计算失败: {str(e)}"
            )
