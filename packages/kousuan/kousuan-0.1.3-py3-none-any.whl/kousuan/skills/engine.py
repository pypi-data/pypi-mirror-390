"""
智能计算器引擎
负责算法自动匹配和执行
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_types import Formula, MathCalculator, CalculationStep, ElementType
from .formula_parser import FormulaParser
from .register import SmartCalculatorReister
from ..base.engine import BaseEngine

operators = ['+', '-', '*', '/', '×', '÷']

class SmartCalculatorEngine(SmartCalculatorReister, BaseEngine):
    """智能计算器引擎 - 算法自动匹配机制"""
    
    def __init__(self):
        super().__init__()

    def is_match_pattern(self, problem: str) -> bool:
        """判断是否为匹配的算术计算问题"""
        ## 是否包含加减乘除运算符号
        if not any(op in problem for op in operators):
            return False
        formula = FormulaParser.parse(problem)
        return any(calculator.is_match_pattern(formula) for calculator in self.calculators)
    
    def fix_number_representation(self, expression) -> str:
        """修正数字表示法"""
        # 如果是整数，直接返回字符串形式
        if isinstance(expression, int):
            return str(expression)
        if isinstance(expression, float):
            # 保留4位精度再变成字符串
            expression = f"{expression:.4f}"
        else:
            expression = str(expression)
        # 如果是0结尾，去掉末尾的所有0
        if '.' in expression:
            expression = expression.rstrip('0').rstrip('.')
        return expression
    def select_all_calculators(self, formula: Formula) -> Dict[str, Any]:
        """获取所有匹配算子的计算结果并进行交叉验证"""
        matching = self.find_matching_calculators(formula)
        
        if not matching:
            return {
                'matched_count': 0,
                'calculators': [],
                'cross_validation': {'passed': False, 'message': '没有匹配的算子'},
                'consensus_result': None
            }
        
        # 按优先级排序
        matching.sort(key=lambda x: x.priority, reverse=True)
        
        calculator_results = []
        results_for_validation = []
        
        for calc in matching:
            try:
                # 执行计算
                result, steps = calc.execute(formula)
                is_valid = calc.validate(formula)
                if not is_valid or not steps or len(steps) == 0:
                    continue
                calculator_info = {
                    'name': calc.name,
                    'description': calc.description,
                    'priority': calc.priority,
                    'result': self.fix_number_representation(result),
                    'steps': steps,
                    'step_count': len(steps),
                    'validation': is_valid,
                    'formula': getattr(calc, 'formula', None),
                    'success': True,
                    'error': None
                }
                
                calculator_results.append(calculator_info)
                results_for_validation.append(result)
                
                print(f"✓ {calc.name}: 结果={result}, 步骤数={len(steps)}")
                
            except Exception as e:
                error_info = {
                    'name': calc.name,
                    'description': calc.description,
                    'priority': calc.priority,
                    'result': None,
                    'steps': [],
                    'step_count': 0,
                    'validation': False,
                    'formula': None,
                    'success': False,
                    'error': str(e)
                }
                
                calculator_results.append(error_info)
                print(f"✗ {calc.name}: 计算失败 - {str(e)}")
        
        # 交叉验证：检查所有成功的计算结果是否一致
        successful_results = [r for r in results_for_validation if r is not None]
        cross_validation = self._perform_cross_validation(successful_results, formula)
        
        # 确定共识结果
        consensus_result = None
        if cross_validation['passed'] and successful_results:
            consensus_result = successful_results[0]  # 所有结果一致时取任意一个
        elif successful_results:
            # 结果不一致时，选择出现次数最多的结果
            from collections import Counter
            result_counts = Counter(successful_results)
            consensus_result = result_counts.most_common(1)[0][0]
        
        return {
            'matched_count': len(matching),
            'successful_count': len([r for r in calculator_results if r['success']]),
            'calculators': calculator_results,
            'cross_validation': cross_validation,
            'consensus_result': consensus_result,
            'formula_type': formula.type,
            'expression': str(formula)
        }
    
    def _perform_cross_validation(self, results: List, formula: Formula) -> Dict[str, Any]:
        """执行交叉验证"""
        if not results:
            return {
                'passed': False,
                'message': '没有可验证的结果',
                'unique_results': [],
                'result_distribution': {}
            }
        
        if len(results) == 1:
            # 只有一个结果时，与直接计算对比
            try:
                direct_result = formula.evaluate_direct()
                is_consistent = abs(results[0] - direct_result) < 1e-10  # 浮点数比较
                return {
                    'passed': is_consistent,
                    'message': '与直接计算结果一致' if is_consistent else '与直接计算结果不一致',
                    'unique_results': [results[0]] if is_consistent else [results[0], direct_result],
                    'result_distribution': {str(results[0]): 1},
                    'direct_calculation': direct_result
                }
            except:
                return {
                    'passed': True,  # 无法直接计算时认为通过
                    'message': '无法进行直接计算验证',
                    'unique_results': [results[0]],
                    'result_distribution': {str(results[0]): 1}
                }
        
        # 多个结果的情况
        from collections import Counter
        
        # 统计结果分布
        result_counts = Counter(results)
        unique_results = list(result_counts.keys())
        
        # 检查是否所有结果都一致
        all_consistent = len(unique_results) == 1
        
        # 计算一致性比例
        total_results = len(results)
        max_count = max(result_counts.values())
        consistency_ratio = max_count / total_results
        
        if all_consistent:
            message = f'所有 {total_results} 个算子结果完全一致'
            passed = True
        elif consistency_ratio >= 0.8:  # 80%以上一致认为通过
            message = f'{max_count}/{total_results} 个算子结果一致 (一致性: {consistency_ratio:.1%})'
            passed = True
        else:
            message = f'结果不一致，最多 {max_count}/{total_results} 个算子一致 (一致性: {consistency_ratio:.1%})'
            passed = False
        
        # 与直接计算结果对比
        try:
            direct_result = formula.evaluate_direct()
            most_common_result = result_counts.most_common(1)[0][0]
            direct_match = abs(most_common_result - direct_result) < 1e-10
            
            if direct_match:
                message += '，且与直接计算一致'
            else:
                message += '，但与直接计算不一致'
                passed = False
        except:
            message += '，无法验证直接计算'
        
        return {
            'passed': passed,
            'message': message,
            'unique_results': unique_results,
            'result_distribution': {str(k): v for k, v in result_counts.items()},
            'consistency_ratio': consistency_ratio,
            'total_calculators': total_results
        }

    def select_best_calculator(self, formula: Formula) -> Optional[MathCalculator]:
        """根据优先级和步骤数选择最佳算子"""
        matching = self.find_matching_calculators(formula)
        
        if not matching:
            return None
        
        # 按优先级排序（高优先级在前）
        matching.sort(key=lambda x: x.priority, reverse=True)
        # 获取最高优先级
        highest_priority = matching[0].priority
        
        # 筛选出最高优先级的算子
        top_priority_calcs = [calc for calc in matching if calc.priority == highest_priority]
        
        if len(top_priority_calcs) == 1:
            return top_priority_calcs[0]
        
        # 如果优先级相同，比较步骤数量
        best_calc = None
        min_steps = float('inf')
        
        for calc in top_priority_calcs:
            try:
                steps = calc.construct_steps(formula)
                print(f"算子 {calc.name} 生成步骤数: {len(steps)}")
                if len(steps) < min_steps:
                    min_steps = len(steps)
                    best_calc = calc
            except:
                continue
        return best_calc
    
    def solve(self, expression: str) -> Dict[str, Any]:
            return self.calculate(expression)
    def solve_all_solutions(self, expression: str) -> Dict[str, Any]:
            return self.select_all_calculators(FormulaParser.parse(expression))
    def format_formula(self, expression) -> Formula:
        return FormulaParser.parse(expression)
    def calculate(self, expression: str) -> Dict[str, Any]:
        """主计算方法"""
        try:
            # 检查空表达式
            if not expression or not expression.strip():
                return {
                    'success': False,
                    'expression': expression,
                    'error': '表达式不能为空',
                    'method': None,
                    'result': None
                }
            
            # 解析表达式
            formula = self.format_formula(expression)
            # 检查表达式是否有效
            if not formula.is_valid_expression():
                return {
                    'success': False,
                    'expression': expression,
                    'error': '无效的表达式',
                    'method': None,
                    'result': None
                }
            
            # 找到最佳算子
            best_calculator = self.select_best_calculator(formula)
            
            if best_calculator is None:
                # 没找到匹配的算子，使用直接计算
                try:
                    direct_result = formula.evaluate_direct()
                    return {
                        'success': True,
                        'expression': expression,
                        'method': '直接计算',
                        'description': '使用标准算术运算',
                        'result': self.format_result(direct_result),
                        'steps': [],
                        'formula_type': formula.type,
                        'validation': True,
                        'priority': 0
                    }
                except:
                    return {
                        'success': False,
                        'expression': expression,
                        'error': '无法计算表达式',
                        'method': None,
                        'result': None
                    }
            
            # 执行计算
            result, steps = best_calculator.execute(formula)
            
            # 验证结果
            is_valid = best_calculator.validate(formula)
            
            return {
                'success': True,
                'expression': expression,
                'method': best_calculator.name,
                'description': best_calculator.description,
                'result': self.format_result(result),
                'steps': steps,
                'name': best_calculator.name,
                'formula': best_calculator.formula,
                'formula_type': formula.type,
                'validation': is_valid,
                'priority': best_calculator.priority
            }
            
        except Exception as e:
            return {
                'success': False,
                'expression': expression,
                'error': str(e),
                'method': None,
                'result': None
            }

    def batch_calculate(self, expressions: List[str]) -> List[Dict[str, Any]]:
        """批量计算"""
        results = []
        for expr in expressions:
            result = self.calculate(expr)
            results.append(result)
        return results
    
    def get_available_methods(self) -> List[Dict[str, Any]]:
        """获取所有可用的速算方法"""
        methods = []
        for calc in self.calculators:
            methods.append({
                'name': calc.name,
                'description': calc.description,
                'priority': calc.priority
            })
        return sorted(methods, key=lambda x: x['priority'], reverse=True)
    
    def calculate_with_cross_validation(self, expression: str) -> Dict[str, Any]:
        """带交叉验证的计算方法"""
        try:
            # 检查空表达式
            if not expression or not expression.strip():
                return {
                    'success': False,
                    'expression': expression,
                    'error': '表达式不能为空',
                    'cross_validation': None
                }
            
            # 解析表达式
            formula = FormulaParser.parse(expression)
            
            # 检查表达式是否有效
            if not formula.is_valid_expression():
                return {
                    'success': False,
                    'expression': expression,
                    'error': '无效的表达式',
                    'cross_validation': None
                }
            
            # 获取所有算子的计算结果
            all_results = self.select_all_calculators(formula)
            
            # 选择最佳算子
            best_calculator = self.select_best_calculator(formula)
            
            # 构建返回结果
            result_data = {
                'success': True,
                'expression': expression,
                'formula_type': formula.type,
                'all_results': all_results,
                'best_method': None,
                'final_result': all_results['consensus_result']
            }
            
            # 添加最佳算子信息
            if best_calculator:
                try:
                    best_result, best_steps = best_calculator.execute(formula)
                    result_data['best_method'] = {
                        'name': best_calculator.name,
                        'description': best_calculator.description,
                        'result': best_result,
                        'steps': best_steps,
                        'priority': best_calculator.priority,
                        'validation': best_calculator.validate(formula)
                    }
                except Exception as e:
                    result_data['best_method'] = {
                        'error': f'最佳算子执行失败: {str(e)}'
                    }
            
            return result_data
            
        except Exception as e:
            return {
                'success': False,
                'expression': expression,
                'error': str(e),
                'cross_validation': None
            }
        
class DivisionRemainderEngine(SmartCalculatorEngine):
    splitor = '······'
    """带余数除法计算引擎"""
    def __init__(self):
        super().__init__()
        self.calculators = [self.get_division_remainder()]
    def format_formula(self, expression) -> Formula:
        formula = FormulaParser.parse(expression)
        if '@' not in formula.original_expression:
            formula.original_expression = expression.replace(' ', '')
        return formula
    def is_match_pattern(self, problem: str) -> bool:
        operators = '><='
        if  ('@×'  in problem or '×@' in problem) and any(op in problem for op in operators):
            return True
        if '······' not in problem:
            return False
        return True
    
class RevertCalculatorEngine(SmartCalculatorEngine):
    """未知数逆运算计算引擎"""
    def __init__(self):
        super().__init__()
        self.calculators = [self.get_revert_calculator()]
    def format_formula(self, expression) -> Formula:
        formula = FormulaParser.parse(expression)
        formula.original_expression = expression.replace(' ', '')
        return formula
    def is_match_pattern(self, problem: str) -> bool:
        if problem and (problem[0] == '@' or '@=' in problem):
            return True
        formula = self.format_formula(problem)
        return any([calculator.is_match_pattern(formula) for calculator in self.calculators])