"""
混合/连续运算计算引擎
"""

from typing import Dict, Any, List, Optional
from .base_types import MixedProblem, MixedResult, MixedCalculator
from .parser import MixedParser
from .registry import MixedCalculatorRegistry
from ..base.engine import BaseEngine



class MixedEngine(BaseEngine):
    """混合运算计算引擎"""
    
    def __init__(self):
        self.registry = MixedCalculatorRegistry()
    
    def is_match_pattern(self, expression: str) -> bool:
        """判断是否为混合/连续运算问题"""
        cleaned_expr = self.clean_expression(expression)
        operators = self.get_operators(cleaned_expr)
        if len(operators) < 2:
            return False  # 至少需要2个运算符才算多次运算
        try:
            problem = MixedParser.parse(cleaned_expr)
            matching = self.registry.find_matching_calculators(problem)
            return len(matching) > 0
        except (ValueError, Exception):
            return False

    def solve(self, expression: str) -> Dict[str, Any]:
        """解决混合运算问题"""
        try:
            # 清理表达式，移除等号和@
            cleaned_expr = expression.replace('=@', '').replace('=', '').replace('@', '').strip()
            if not cleaned_expr:
                return {
                    'success': False,
                    'expression': expression,
                    'error': '表达式为空',
                    'name': None,
                    'result': None
                }
            
            # 统一运算符
            cleaned_expr = cleaned_expr.replace('x', '*').replace('×', '*').replace('÷', '/')
            
            # 解析表达式
            problem = MixedParser.parse(cleaned_expr)
            
            # 找到最佳算子
            calculator = self.registry.get_best_calculator(problem)
            
            if calculator is None:
                return {
                    'success': False,
                    'expression': expression,
                    'error': '未找到匹配的算子',
                    'name': None,
                    'result': None
                }
            
            # 执行计算
            result = calculator.solve(problem)
            
            if result.success:
                return {
                    'success': True,
                    'expression': expression,
                    'name': calculator.name,
                    'problem': expression,
                    'description': calculator.description,
                    'result': self.format_result(result.result),
                    'steps': result.steps,
                    'step_count': result.step_count,
                    'formula': result.formula,
                    'validation': result.validation,
                    'priority': calculator.priority,
                    'technique_used': result.technique_used
                }
            else:
                return {
                    'success': False,
                    'expression': expression,
                    'name': calculator.name,
                    'error': result.error,
                    'result': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'expression': expression,
                'error': f"计算失败: {str(e)}",
                'name': None,
                'result': None
            }
    
    def solve_all_solutions(self, expression: str) -> Dict[str, Any]:
        """获取所有可能的解决方案"""
        try:
            problem = MixedParser.parse(expression)
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
                            'name': calculator.name,
                            'description': calculator.description,
                            'result': result.result,
                            'steps': [self._format_step(step) for step in result.steps],
                            'step_count': result.step_count,
                            'formula': result.formula,
                            'validation': result.validation,
                            'priority': calculator.priority,
                            'technique_used': result.technique_used
                        })
                except Exception as e:
                    solutions.append({
                        'name': calculator.name,
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
