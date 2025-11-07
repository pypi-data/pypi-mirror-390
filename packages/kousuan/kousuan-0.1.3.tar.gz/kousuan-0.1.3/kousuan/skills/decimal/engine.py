## 实现小数计算表达式的格式、匹配和一般处理规则

from ..engine import SmartCalculatorEngine

# 导入所有小数计算算子
from .decima_calculator import DecimaCalculator
from .decimal_align_addition import DecimalAlignAddition
from .decimal_round_addition import DecimalRoundAddition
from .decimal_integer_method import DecimalIntegerMethod
from .decimal_divisor_integer import DecimalDivisorInteger
from .decimal_scale_multiply import DecimalScaleMultiply
from .decimal_distribution_multiply import DecimalDistributionMultiply

# 导入Formula类
from ..formula_parser import FormulaParser

Calculators = [
    DecimalScaleMultiply,
    DecimalIntegerMethod,
    DecimalDivisorInteger,
    DecimalRoundAddition,
    DecimalDistributionMultiply,
    DecimalAlignAddition,
    DecimaCalculator
]

operators = ['+', '-', '×', '÷', '*', '/']

class DecimalCalculatorEngine(SmartCalculatorEngine):
   """智能计算器引擎 - 算法自动匹配机制"""
    
   def __init__(self):
      super().__init__()
      self.calculators = [calc() for calc in Calculators]

   def is_match_pattern(self, problem: str) -> bool:
        """判断是否为匹配小数计算的表达式"""
        ## 是否包含加减乘除运算符号
        if not any(op in problem for op in operators):
            return False
        ## 表达式是否包含小数计算模式
        if '.' not in problem:
            return False
        formula = FormulaParser.parse(problem)
        for calculator in self.calculators:
            if calculator.is_match_pattern(formula=formula):
                return True
        return False

   def resolve(self, expression: str):
      """解析并计算小数表达式，返回计算步骤和结果"""
      formula = FormulaParser.parse(expression)
      
      # 按优先级排序算子
      sorted_calculators = sorted(
         self.calculators,
         key=lambda c: c.priority,
         reverse=True
      )

      results = []
      for calculator in sorted_calculators:
         if calculator.is_match_pattern(formula):
               steps = calculator.construct_steps(formula)
               result = steps[-1].result if len(steps) > 0 else None
               result = self.format_result(result)
               results.append({
                  'success': True,
                  'name': calculator.name,
                  'description': calculator.description,
                  'formula': calculator.formula,
                  'steps': steps,
                  'result': result
               })
      return {
         'success': True,
         'calculators': results
      }