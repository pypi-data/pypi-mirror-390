"""
工具函数
包含格式化输出等辅助功能
"""

from typing import Dict, Any


def format_calculation_result(result: Dict[str, Any]) -> str:
    """格式化计算结果为可读字符串"""
    if not result['success']:
        return f"❌ 计算失败: {result['expression']} - {result.get('error', '未知错误')}"
    
    output = []
    output.append(f"📊 算式: {result['expression']}")
    output.append(f"🎯 方法: {result['method']}")
    
    if 'description' in result:
        output.append(f"📝 说明: {result['description']}")

    # 提前给出公式
    if 'formula' in result and result['formula']:
        output.append(f"📐 公式: {result['formula']}")

    output.append(f"🔢 结果: {result['result']}")
    
    if result.get('validation'):
        output.append("✅ 验证: 通过")
    else:
        output.append("⚠️  验证: 需要检查")
    
    if 'steps' in result and result['steps']:
        output.append("\n📋 计算步骤:")
        for i, step in enumerate(result['steps'], 1):
            output.append(f"  {i}. {step.description}")
            if step.formula:
                output.append(f"     公式: {step.formula}")
            output.append(f"     结果: {step.result}")
    
    return '\n'.join(output)



def get_multiplication_table(number: int, limit: int = 10):
    """
    Generate multiplication table for a given number

    Args:
        number: The base number
        limit: The maximum multiplier (default: 10)

    Returns:
        List of calculation results with multiplication table
    """
    table = []
    steps = [f"Generating multiplication table for {number}:"]
    
    for i in range(1, limit + 1):
        expression = f"{number} × {i} = {number * i}"
        table.append(expression)
        steps.append(expression)
    
    return [{
        "value": table,
        "explanation": f"Multiplication table for {number} up to {limit}",
        "steps": steps
    }]