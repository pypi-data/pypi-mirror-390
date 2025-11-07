"""
智能速算规则识别程序主入口
基于速算手册知识点，自动识别最匹配的速算方法并执行演算过程
"""

import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os
import argparse

from .engine import SmartCalculatorEngine
from .utils import format_calculation_result
from .mixure_calc import ExpressionOptimizer
import re


def count_operators(expression: str) -> int:
    """计算表达式中的运算符数量"""
    # 移除空格
    expr = expression.replace(" ", "")
    # 计算运算符数量（排除负号）
    operators = re.findall(r'[+\-*x/]', expr)
    # 排除开头的负号
    if expr.startswith('-'):
        operators = operators[1:]
    # 排除数字中间的负号（如 1e-5）
    operator_count = 0
    for i, char in enumerate(expr):
        if char in '+-*x/' and i > 0:
            prev_char = expr[i-1]
            if not (char == '-' and prev_char in 'eE'):
                operator_count += 1
    return operator_count


def is_mixed_operation(expression: str) -> bool:
    """判断是否为混合运算（多个运算符）"""
    return count_operators(expression) > 1


def is_addition_only(expression: str) -> bool:
    """判断是否仅包含加法运算"""
    expr = expression.replace(" ", "").replace("-", "+-")
    if expr.startswith("+-"):
        expr = expr[1:]
    # 检查是否只有加号和数字
    return all(c.isdigit() or c in '.+' or c == '-' for c in expr) and '+' in expr


def smart_calculate(expression: str) -> dict:
    """智能计算路由：根据表达式复杂度选择合适的处理引擎"""
    
    # 创建引擎实例
    single_engine = SmartCalculatorEngine()
    mixed_optimizer = ExpressionOptimizer()
    
    try:
        # 判断表达式类型
        if is_mixed_operation(expression):
            # 多步骤混合运算，使用混合运算优化器
            print("🔄 检测到混合运算，使用混合运算优化器...")
            
            # 混合运算优化器会直接打印结果，我们需要捕获其输出
            import io
            import contextlib
            
            # 捕获打印输出
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                mixed_optimizer.optimize(expression)
            
            captured_output = output_buffer.getvalue()
            
            # 解析结果（简化版，主要用于演示）
            lines = captured_output.split('\n')
            result_line = [line for line in lines if line.startswith('最终结果:')]
            if result_line:
                result_str = result_line[0].replace('最终结果:', '').strip()
                try:
                    final_result = float(result_str)
                except:
                    final_result = None
            else:
                final_result = None
            
            return {
                'success': True,
                'expression': expression,
                'method': '混合运算优化',
                'description': '基于策略库的多步骤混合运算优化',
                'result': final_result,
                'engine_type': 'mixed',
                'detailed_output': captured_output
            }
            
        else:
            # 单个运算符或简单运算，使用单算子引擎
            print("⚙️  使用单算子引擎处理...")
            result = single_engine.calculate_with_cross_validation(expression)
            result['engine_type'] = 'single'
            return result
            
    except Exception as e:
        return {
            'success': False,
            'expression': expression,
            'error': f'计算错误: {str(e)}',
            'method': None,
            'result': None
        }


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='智能速算规则识别程序')
    parser.add_argument('expression', nargs='?', help='要计算的表达式')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
    parser.add_argument('-b', '--batch', help='批量计算文件')
    parser.add_argument('-m', '--methods', action='store_true', help='显示所有可用方法')
    parser.add_argument('-t', '--test', action='store_true', help='运行测试用例')
    
    args = parser.parse_args()
    
    # 创建计算器引擎
    engine = SmartCalculatorEngine()
    
    if args.methods:
        # 显示所有可用方法
        print("🧮 可用的速算方法:")
        methods = engine.get_available_methods()
        for method in methods:
            print(f"  • {method['name']} (优先级: {method['priority']})")
            print(f"    {method['description']}")
        return
    
    if args.test:
        # 运行测试用例
        test_cases = [
            "9+5",              # 凑十法（单算子）
            "13-8",             # 破十法（单算子）
            "36*5",             # 乘5速算（单算子）
            "63*67",            # 同头尾合十（单算子）
            "34*74",            # 头合十尾相同（单算子）
            "125+95+75+5",      # 混合加法运算（混合运算优化器）
            "36+1.2+14.8",      # 小数凑整（混合运算优化器）
            "25+37+75",         # 凑整成十（混合运算优化器）
            "24+36*5+16+20",    # 包含乘法的混合运算（混合运算优化器）
            "48/2+25+75+52",    # 包含除法的混合运算（混合运算优化器）
            "100-12*3+25+15",   # 包含减法和乘法的混合运算（混合运算优化器）
        ]
        
        print("🧪 运行测试用例:")
        for expr in test_cases:
            print(f"\n📊 表达式: {expr}")
            result = smart_calculate(expr)
            if result.get('engine_type') != 'mixed':
                # 对于单算子引擎，使用原有格式化输出
                print(f"{format_calculation_result(result)}")
            print("-" * 60)
        return
    
    if args.batch:
        # 批量计算
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                expressions = [line.strip() for line in f if line.strip()]
            
            print(f"📁 批量计算 {len(expressions)} 个表达式:")
            
            for i, expr in enumerate(expressions, 1):
                print(f"\n[{i}/{len(expressions)}] 表达式: {expr}")
                result = smart_calculate(expr)
                if result.get('engine_type') != 'mixed':
                    print(f"{format_calculation_result(result)}")
                print("-" * 40)
                
        except FileNotFoundError:
            print(f"❌ 文件未找到: {args.batch}")
        return
    
    if args.interactive:
        # 交互模式
        print("🧮 智能速算计算器 - 交互模式")
        print("支持单算子速算和混合运算优化")
        print("输入算式进行计算，输入 'quit' 退出，输入 'methods' 查看可用方法")
        
        while True:
            try:
                expr = input("\n请输入算式: ").strip()
                
                if expr.lower() == 'quit':
                    print("👋 再见！")
                    break
                elif expr.lower() == 'methods':
                    methods = engine.get_available_methods()
                    print("\n🧮 可用的速算方法:")
                    for method in methods:
                        print(f"  • {method['name']} (优先级: {method['priority']})")
                        print(f"    {method['description']}")
                    print("\n🔧 混合运算优化策略:")
                    print("  • 凑整成百 (奖励: +5)")
                    print("  • 凑整成十 (奖励: +4)")  
                    print("  • 小数凑整 (奖励: +2)")
                    print("  • 补数法 (奖励: +3)")
                    continue
                elif not expr:
                    continue
                
                result = smart_calculate(expr)
                if result.get('engine_type') != 'mixed':
                    print(f"\n{format_calculation_result(result)}")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except EOFError:
                break
    
    elif args.expression:
        # 单个表达式计算
        result = smart_calculate(args.expression)
        if result.get('engine_type') != 'mixed':
            print(format_calculation_result(result))
    
    else:
        # 默认显示帮助
        parser.print_help()


if __name__ == "__main__":
    main()