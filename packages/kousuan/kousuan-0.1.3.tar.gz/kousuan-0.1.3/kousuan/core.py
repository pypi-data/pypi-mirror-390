"""
Core module for kousuan package
Provides various mental arithmetic calculation techniques
"""

import math
import re
import os
from typing import Union, List, Dict, Any
from kousuan.skills import SmartCalculatorEngine, DivisionRemainderEngine, RevertCalculatorEngine, AICalculator, CalculationStep

# 导入小数计算功能
from kousuan.skills.decimal.engine import DecimalCalculatorEngine

# 导入单位换算引擎
from kousuan.units.unit_engine import UnitConversionEngine

from kousuan.fraction.engine import FractionEngine

from kousuan.mixed.engine import MixedEngine

env = os.environ
configuration = {
    "name": "kousuan_core",
    "llm_model":  env.get("OPENAI_API_BASE", "gpt-5-mini"),
    "base_url": env.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
    "api_key": env.get("OPENAI_API_KEY", "")
}

def update_configuration(new_config: Dict[str, Any]):
    """Update configuration settings"""
    global configuration
    configuration.update(new_config)

def generate_ai_calculation(expression: str, calc_skills: str = '') -> Dict[str, Any]:
    ai_calculator = AICalculator(model=configuration["llm_model"], base_url=configuration["base_url"], api_key=configuration["api_key"])
    return ai_calculator.resolve_question(expression, calc_skills=calc_skills)

def calculate(expression: str) -> Dict[str, Any]:
    smartEngine = SmartCalculatorEngine()
    unitEngine = UnitConversionEngine()
    # 匹配表达式规则
    if unitEngine.is_match_pattern(expression):
        return unitEngine.solve(expression)
    return smartEngine.solve(expression)

def is_compare_expression(expression: str) -> tuple[bool, Union[str, int]]:
    """判断是否为比较表达式"""
    """特征：表达式不包含等号"="，但是有@符号，而去@符号后面紧跟数字
    需要返回@后的数字
    """
    if '=' in expression:
        return False, 0
    match = re.search(r'@([-]?\d+)', expression)
    if match:
        return True, match.group(1)
    return False, 0

def decorate_comparison_result(calculators, target_value: Union[str, int, None]) -> List[Dict[str, Any]]:
    if target_value is None:
        return calculators
    for calc in calculators:
        result = calc.get('result', None)
        if result is not None:
            try:
                steps = calc.get('steps', [])
                target_value = calc.get('target_value', '') or target_value
                numeric_result = float(result)
                target_numeric = float(target_value)
                if math.isclose(numeric_result, target_numeric, rel_tol=1e-9):
                    comparison = "="
                elif numeric_result < target_numeric:
                    comparison = "<"
                else:
                    comparison = ">"
                calc['result'] = comparison
                calc['value'] = result
                step = CalculationStep(
                    description="比较结果与目标值的大小",
                    operation="比较大小",
                    result=f"{numeric_result} {comparison} {target_numeric}"
                )
                steps.append(step)
            except (ValueError, TypeError):
                calc['comparison'] = ""
        else:
            calc['comparison'] = "无法比较，结果为空"
    return calculators

def compare_resolve(expression: str) -> List[Dict[str, Any]]:
    segs = expression.split('@')
    if len(segs) != 2:
        return []
    left_raw = segs[0].strip()
    right_raw = segs[1].strip()

    def safe_eval(val: str):
        try:
            # 支持表达式计算，兼容 x、X、÷、等
            val = val.replace('x', '*').replace('X', '*').replace('÷', '/').replace('＝', '=')
            # 只允许数字、运算符和小数点
            if not re.match(r'^[\d\-\+\*/\.\(\) ]+$', val):
                return float('nan')
            return eval(val, {"__builtins__": None}, {})
        except Exception:
            return float('nan')

    left = safe_eval(left_raw)
    right = safe_eval(right_raw)
    if math.isnan(left) or math.isnan(right):
        return []
    result = '='
    if left < right:
        result = '<'
    elif left > right:
        result = '>'
    steps = [
        {
            'description': '对比表达式或数字的大小',
            'operation': '对比大小',
            'result': f'{left} {result} {right}',
        }
    ]
    calculator = {
        'success': True,
        'expression': expression,
        'name': '比较大小',
        'description': '表达式/数字比较',
        'result': result,
        'steps': steps,
        'validation': True,
        'priority': 0
    }
    return [calculator]

def decimal_replacer(match):
    """小数点后超过6位的数字处理函数"""
    number_str = match.group(1)
    # 保留小数点后6位
    trimmed_number = f"{float(number_str):.6f}"
    # 去除多余的0
    if '.' in trimmed_number:
        trimmed_number = trimmed_number.rstrip('0').rstrip('.')
    return trimmed_number
def trim_decimal(text: str) -> str:
    """处理小数点精度过高的情况"""
    ## 删除小数点后超过6位的数字
    pattern = r'(?<!#)(\d+\.\d{6})\d+(?!#)'
    text = re.sub(pattern, decimal_replacer, text)
    return text

def format_fraction_text(text: str) -> str:
    """提取文本中分数 1/3 为 latex 格式 #frac{1}{3}#"""
    ## 匹配所有分数形式的文本
    import re
    def replacer(match):
        numer = match.group(1)
        denom = match.group(2)
        return f" #frac{{{numer}}}{{{denom}}}# "
    if '.' in text:
        text = trim_decimal(text)
    pattern = r'(?<!#)\\?(\d+)\s*/\s*(\d+)(?!#)'
    formatted_text = re.sub(pattern, replacer, text)
    return formatted_text.strip()
    
def dictionary(func):
    """Decorator to convert function output to dictionary"""
    def wrapper(*args, **kwargs):
        calculators = func(*args, **kwargs)
        for calculator in calculators:
            if not calculator or len(calculator.get('steps', [])) == 0:
                continue
            step_dicts = []
            result = calculator.get('result', '')
            formula = calculator.get('formula', '')
            if formula:
                calculator['formula'] = format_fraction_text(formula)
            latexResult = calculator.get('latexResult')
            if latexResult:
                calculator['result'] = latexResult
                
            # 如果是分数类型，转换为字符串
            for step in calculator['steps']:
                if hasattr(step, 'description'):
                    step_dict = {
                        'description': format_fraction_text(step.description),
                        'operation': step.operation,
                        'result': format_fraction_text(str(step.result)),
                    }
                    if step.formula:
                        step_dict['formula'] = format_fraction_text(step.formula)
                else:
                    step_dict = step
                step_dicts.append(step_dict)
            calculator['steps'] = step_dicts
        return calculators
    return wrapper

@dictionary
def ask_ai(expression: str, answer: str = '') -> List[Dict[str, Any]]:
    skills = []
    if answer:
        skills.insert(0, f"目标答案是 {answer} 。")
    result = generate_ai_calculation(expression, calc_skills='\n- '.join(skills))
    if result and result.get('success', False):
        result['engine'] = 'AICalculator'
        return [result]
    return []
    

@dictionary
def resolve(expression: str, answer: str = '', optimize: bool = False) -> List[Dict[str, Any]]:
    smartEngine = SmartCalculatorEngine()
    unitEngine = UnitConversionEngine()
    decimalEngine = DecimalCalculatorEngine()
    fractionEngine = FractionEngine()
    mixedEngine = MixedEngine()
    divisionRemainderEngine = DivisionRemainderEngine()
    revertEngine = RevertCalculatorEngine()
    skills = []
    is_comparion, target_value = is_compare_expression(expression)
    if not is_comparion:
        target_value = None
    # 匹配表达式规则
    if is_comparion:
        r = compare_resolve(expression)
        if r and len(r) > 0:
            return r
    # 如果表达式纯数字，转化为单位换算
    if re.match(r'^\d+(\.\d+)?0000$', expression.strip()):
        expression = f"{expression}=@万"
    if unitEngine.is_match_pattern(expression):
        result = unitEngine.solve(expression)
        result['engine'] = 'UnitConversionEngine'
        if result and result.get('success', False):
            return decorate_comparison_result([result], target_value)
    if '#frac' in expression and fractionEngine.is_match_pattern(expression):
        result = fractionEngine.solve(expression)
        if result and result.get('success', False):
            result['engine'] = 'FractionEngine'
            return [result]
    elif ':' in expression and fractionEngine.is_match_pattern(expression):
        result = fractionEngine.solve(expression)
        if result and result.get('success', False):
            result['engine'] = 'FractionEngine'
            return [result]
    elif divisionRemainderEngine.is_match_pattern(expression):
        result = divisionRemainderEngine.solve(expression)
        if result and result.get('success', False):
            result['engine'] = 'DivisionRemainderEngine'
            return decorate_comparison_result([result], target_value)
    elif '.' in expression and decimalEngine.is_match_pattern(expression):
        result = decimalEngine.resolve(expression)
        if result and result.get('success', False):
            result['engine'] = 'DecimalCalculatorEngine'
            return decorate_comparison_result(result.get('calculators', []), target_value)
    elif mixedEngine.is_match_pattern(expression):
        result = mixedEngine.solve(expression)
        ## 如果提供了答案，则进行结果校验
        if answer and not (result.get('result', '') == answer):
                result['success'] = False
        if result and result.get('success', False):
            result['engine'] = 'MixedEngine'
            return decorate_comparison_result([result], target_value)
    
    if revertEngine.is_match_pattern(expression):
        result = revertEngine.solve(expression)
        if result and result.get('success', False):
            result['engine'] = 'RevertCalculatorEngine'
            return [result]
    elif 'frac' not in expression and smartEngine.is_match_pattern(expression):
        result = smartEngine.solve_all_solutions(expression) or {}
        if result:
            calculators = result.get('calculators', [])
            if not optimize:
                return decorate_comparison_result(calculators, target_value)
            else:
                skill = [ calc for calc in calculators]
                skills.extend(skill)
            if len(calculators) > 0 and len(calculators[0].get('steps', [])) > 0:
                return  calculators
    
    if optimize and len(expression) > 3:
        if answer:
            skills.insert(0, f"目标答案是 {answer} 。")
        calc_skills = '\n- '.join(skills)
        result = generate_ai_calculation(expression, calc_skills=calc_skills)
        if result and result.get('success', False):
            result['engine'] = 'AICalculator'
            return [result]
    return []