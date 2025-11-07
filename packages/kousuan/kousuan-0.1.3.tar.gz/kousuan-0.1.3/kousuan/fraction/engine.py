"""
分数计算引擎
"""

from typing import Dict, Any, List, Optional
from .base_types import FractionProblem, FractionResult, FractionStep
from .parser import FractionParser
from .registry import FractionCalculatorRegistry
from fractions import Fraction
from ..base.engine import BaseEngine


class FractionEngine(BaseEngine):
    """分数计算引擎"""
    
    def __init__(self):
        self.registry = FractionCalculatorRegistry()
    
    def is_match_pattern(self, expression: str) -> bool:
        """判断是否为分数计算问题"""
        try:
            problem = FractionParser.parse(expression)
            matching = self.registry.find_matching_calculators(problem)
            return len(matching) > 0
        except (ValueError, Exception):
            return False
        
    def solve(self, expression: str) -> Dict[str, Any]:
        """解决分数计算问题"""
        try:
            # 解析表达式
            problem = FractionParser.parse(expression)
            
            # 找到最佳算子
            calculator = self.registry.get_best_calculator(problem)
            
            if calculator is None:
                return {
                    'success': False,
                    'expression': expression,
                    'error': '未找到匹配的算子',
                    'method': None,
                    'result': None
                }
            
            # 执行计算
            result = calculator.solve(problem)
            finalResult = result.result
            latexResult = str(finalResult)
            if isinstance(finalResult, Fraction):
                if finalResult.denominator == 1:
                    # 整数结果，直接输出整数形式
                    latexResult = str(finalResult.numerator)
                else:
                    # 提取分数整数
                    if abs(finalResult.numerator) > finalResult.denominator:
                        whole_part = finalResult.numerator // finalResult.denominator
                        remainder = abs(finalResult.numerator) % finalResult.denominator
                        latexResult = f"#{whole_part}frac{{{remainder}}}{{{finalResult.denominator}}}#"
                        post_steps = FractionStep(
                            description=f"约分并提取整数部分",
                            operation="提取整数带分数",
                            result=latexResult
                        )
                        result.steps.append(post_steps)
                        result.step_count += 1
                    else:
                        latexResult = f"#frac{{{finalResult.numerator}}}{{{finalResult.denominator}}}#"
            
            if result.success:
                result_value = self.format_result(result.result)
                latexResult = self.format_result(latexResult)
                return {
                    'success': True,
                    'expression': expression,
                    'name': calculator.name,
                    'description': calculator.description,
                    'result': result_value,
                    'latexResult': latexResult,
                    'steps': result.steps,
                    'step_count': result.step_count,
                    'formula': result.formula,
                    'validation': result.validation,
                    'priority': calculator.priority
                }
            else:
                return {
                    'success': False,
                    'expression': expression,
                    'method': calculator.name,
                    'error': result.error,
                    'result': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'expression': expression,
                'error': f"计算失败: {str(e)}",
                'method': None,
                'result': None
            }
    
    def solve_all_solutions(self, expression: str) -> Dict[str, Any]:
        """获取所有可能的解决方案"""
        try:
            problem = FractionParser.parse(expression)
            matching = self.registry.find_matching_calculators(problem)
            
            if not matching:
                return {
                    'success': False,
                    'expression': expression,
                    'error': '未找到匹配的算子',
                    'solutions': []
                }
            
            solutions = []
            for calculator in matching:
                try:
                    result = calculator.solve(problem)
                    if result.success:
                        solutions.append({
                            'method': calculator.name,
                            'description': calculator.description,
                            'result': self.format_result(result.result),
                            'steps': [self._format_step(step) for step in result.steps],
                            'step_count': result.step_count,
                            'formula': result.formula,
                            'validation': result.validation,
                            'priority': calculator.priority
                        })
                except Exception as e:
                    solutions.append({
                        'method': calculator.name,
                        'error': str(e),
                        'success': False
                    })
            
            return {
                'success': True,
                'expression': expression,
                'solutions': solutions,
                'solution_count': len(solutions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'expression': expression,
                'error': f"批量计算失败: {str(e)}",
                'solutions': []
            }
    
    def _format_step(self, step) -> Dict[str, Any]:
        """格式化计算步骤"""
        return {
            'description': step.description,
            'operation': step.operation,
            'inputs': step.inputs,
            'result': step.result,
            'formula': step.formula,
            'validation': step.validation,
            'meta': step.meta
        }
    
    def get_available_methods(self) -> List[Dict[str, Any]]:
        """获取所有可用的算子"""
        methods = []
        for calc in self.registry.get_all_calculators():
            methods.append({
                'name': calc.name,
                'description': calc.description,
                'priority': calc.priority
            })
        return methods
    
    def batch_solve(self, expressions: List[str]) -> List[Dict[str, Any]]:
        """批量解决问题"""
        results = []
        for expr in expressions:
            result = self.solve(expr)
            results.append(result)
        return results
