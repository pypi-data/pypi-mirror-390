"""
Command-line interface for kousuan package
"""
import argparse
from fractions import Fraction
import sys
import json
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kousuan.skills import SmartCalculatorEngine

# 导入单位换算引擎
from kousuan.units.unit_engine import UnitConversionEngine

from kousuan.fraction.engine import FractionEngine

# 导入混合运算引擎
from kousuan.mixed.engine import MixedEngine

from kousuan.core import resolve, ask_ai, update_configuration

def main():
    """Main entry point for the CLI"""
    update_configuration({'llm_model': 'gpt-4o-2024-11-20'})
    if len(sys.argv) == 2 and sys.argv[1].strip() != "calc":
        test_exp(sys.argv[1])
        return
    
    parser = argparse.ArgumentParser(
        description="Kousuan Skill - Mental Arithmetic Calculation Tools",
        prog="kousuan"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Calc skills
    calc_parser = subparsers.add_parser("calc", help="calcuate math problems")
    calc_parser.add_argument("expression", nargs="+", help="expression to calculate e.g., '2+2'")
    calc_parser.add_argument("--all", action="store_true", default=True, help="Output result in JSON format")
    calc_parser.add_argument("--json", action="store_true", help="Output result in JSON format")

    # Ask AI 
    ask_parser = subparsers.add_parser("ask", help="Ask AI for help on math problems")
    ask_parser.add_argument("expression", nargs="+", help="Question to ask AI")
    ask_parser.add_argument("--all", action="store_true", default=True, help="Output result in JSON format")
    ask_parser.add_argument("--json", action="store_true", help="Output result in JSON format")

    # Units command - 新增单位换算命令
    units_parser = subparsers.add_parser("units", help="Unit conversion calculator")
    units_parser.add_argument("expression", nargs="+", help="Unit conversion expression (e.g., '450 秒 =@分')")
    units_parser.add_argument("--json", action="store_true", help="Output result in JSON format")

    # Fraction command - 新增分数计算命令
    fraction_parser = subparsers.add_parser("frac", help="Fraction calculator")
    fraction_parser.add_argument("expression", nargs="+", help="Fraction expression to calculate (e.g., '#frac{1}{2} + #frac{1}{3}')")
    fraction_parser.add_argument("--json", action="store_true", help="Output result in JSON format")

    # Mixed command - 新增混合运算命令
    mixed_parser = subparsers.add_parser("mixed", help="Mixed arithmetic calculator")
    mixed_parser.add_argument("expression", nargs="+", help="Mixed arithmetic expression (e.g., '2+3*4' or '(5+3)*2')")
    mixed_parser.add_argument("--json", action="store_true", help="Output result in JSON format")

    args = parser.parse_args()
    if not args.command and len(sys.argv) == 2:
        test_exp(sys.argv[1])
        return
    elif not args.command:
        parser.print_help()
        return

    try:
        if args.command == "calc":
            handle_calc_command(args)
        elif args.command == "ask":
            handle_ask_command(args)
        elif args.command == "units":
            handle_units_command(args)
        elif args.command == "frac":
            handle_fraction_command(args)
        elif args.command == "mixed":
            handle_mixed_command(args)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def print_result(result, as_json: bool):
    expression = result.get('problem', '') or result.get('expression', '')
    if as_json:
        valueResult = result.get('result', '')
        result_unit = result.get('result_unit', '')
        if isinstance(valueResult, Fraction):
            ## 使用latex格式输出分数
            result_unit = result.get('latexResult', '')
            valueResult = str(valueResult)
        # JSON格式输出
        output_data = {
            "expression": expression,
            "success": result.get('success'),
            "result": valueResult,
            "name": result.get('name'),
            "result_unit": result_unit,
            "unit_type": result.get('unit_type'),
            "description": result.get('description'),  # 使用新字段名
            "formula": result.get('formula'),  # 添加综合公式字段
            "validation": result.get('validation', False),
        }
        steps = result.get('steps', [])
        if len(steps) > 0 and hasattr(steps[0], 'to_dict'):
            output_data["steps"] = [step.to_dict() for step in steps]
        else:
            output_data["steps"] = steps
        output_data["step_count"] = len(steps)
    
        if not result.get('success'):
            output_data["error"] = result.get('error', 'Unknown error')
        
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    
    else:
        # 普通格式输出
        if result.get('success'):
            print(f"输入: {expression}")
            print(f"结果: {result['result']} {result.get('result_unit', '')}")
            
            if result.get('name'):
                print(f"算法名称: {result['name']}")
            if result.get('description'):
                print(f"算法描述: {result['description']}")
            if result.get('formula'):
                print(f"换算公式: {result['formula']}")
            if result.get('unit_type'):
                print(f"单位类型: {result['unit_type']}")
            steps = result.get('steps', [])
            if steps:
                print(f"\n计算步骤 (共{len(steps)}步):")
                print("-" * 40)
                for i, step in enumerate(steps, 1):
                    print(f"{i}. {step['description']}")
                    print(f"   操作: {step['operation']}")
                    print(f"   结果: {step['result']}")
                    print(f"   公式: {step.get('formula', '')}")
                    print()
        else:
            print(f"错误: {result.get('error', 'Unknown error')}")
            print(f"输入: {expression}")
            sys.exit(1)

def handle_ask_command(args):
    """处理Ask AI命令"""
    # 将参数列表重新组合为表达式字符串
    expression = " ".join(args.expression)
    try:
        # 求解问题
        results = ask_ai(expression)
        for result in results:
            print_result(result, args.json)
    except Exception as e:
        print(f"处理错误: {e}")
        print(f"输入: {expression}")
        sys.exit(1)

def handle_units_command(args):
    """处理单位换算命令"""
    # 将参数列表重新组合为表达式字符串
    expression = " ".join(args.expression)
    # 创建单位换算引擎
    engine = UnitConversionEngine()
    try:
        # 求解单位换算问题
        result = engine.solve(expression)

        print_result(result, args.json)
    except Exception as e:
        print(f"处理错误: {e}")
        print(f"输入: {expression}")
        sys.exit(1)

def handle_fraction_command(args):
    """处理分数计算命令"""
    # 将参数列表重新组合为表达式字符串
    expression = " ".join(args.expression)
    # 创建分数计算引擎
    engine = FractionEngine()
    try:
        # 求解分数计算问题
        result = engine.solve(expression)
        print_result(result, args.json)
    except Exception as e:
        print(f"处理错误: {e}")
        print(f"输入: {expression}")
        sys.exit(1)

def handle_mixed_command(args):
    """处理混合运算命令"""
    # 将参数列表重新组合为表达式字符串
    expression = " ".join(args.expression)
    # 创建混合运算引擎
    engine = MixedEngine()
    try:
        # 求解混合运算问题
        result = engine.solve(expression)
        print_result(result, args.json)
    except Exception as e:
        print(f"处理错误: {e}")
        print(f"输入: {expression}")
        sys.exit(1)

def handle_calc_command(args):
    """处理计算命令"""
    # 将参数列表重新组合为表达式字符串
    expression = " ".join(args.expression)
    # 创建单位换算引擎
    engine = SmartCalculatorEngine()
    try:
        # 求解单位换算问题
        if args.all:
            results = resolve(expression, optimize=False)
            for result in results:
                print_result(result, args.json)
        else:
            result = engine.solve(expression)
            print_result(result, args.json)
    except Exception as e:
        print(f"处理错误: {e}")
        print(f"输入: {expression}")
        sys.exit(1)

def test_unit():
    # 调试混合运算引擎
    from kousuan.units.unit_engine import UnitConversionEngine
    engine = UnitConversionEngine()
    
    test_expressions = [
        # "20-12/4",   # 应该是17（除法优先）
        # "10-5+5=@",  # 纯加减
        # "10+5-5",    # 纯加减
        # "10+5+5"    # 纯加减
    ]
    
    for expr in test_expressions:
        is_match = engine.is_match_pattern(expr)
        if not is_match:
            print(f"Expression '{expr}' not matches unit conversion pattern.")
            break
        print(f"Testing expression: {expr}")
        result = engine.solve(expr)
        print_result(result, as_json=True)
        print("\n" + "="*50 + "\n")

def test_exp(expr: str, answer : str = ''):
    results = resolve(expr, optimize=True, answer=answer)
    print("\n" + "="*20 +  " 测试开始 " + "="*20 + "\n")
    for result in results:
        print_result(result, as_json=True)
    print("\n" + "="*50 + "\n")

def test():
    import time
    update_configuration({'llm_model': 'gpt-4o-2024-11-20'})
    start_timestamp = time.time()
    test_exp('西瓜每千克3.5元，香蕉每千克4.5元，都买了2千克，问一共多少钱？')
    end_timestamp = time.time()
    print(f"测试耗时: {end_timestamp - start_timestamp:.6f}秒")

if __name__ == "__main__":
    ## 判断参数个数
    if len(sys.argv) < 2:
        print("请提供表达式作为参数")
        test()
        sys.exit(1)

