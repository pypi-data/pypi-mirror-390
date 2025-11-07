import traceback
from typing import Any, Dict, Optional
from dataclasses import dataclass

operators = set("+-×÷x*/")

@dataclass
class ConversionStep:
    """单位换算步骤"""
    description: str
    operation: str
    result: str  # 修改字段名以保持一致性
    formula: Optional[str] = None
    
    def __str__(self):
        return f"{self.description}: → {self.result}"
    def to_dict(self) -> Dict[str, Any]:
        result = self.result
        return {
            "description": self.description,
            "operation": self.operation,
            "result": result,
            "formula": self.formula
        }

class BaseEngine:
    pre_steps = []
    post_steps = []
    """基础计算引擎"""
    def __init__(self) -> None:
        pass
    def add_pre_step(self, step: Any) -> None:
        """添加计算前置步骤"""
        self.pre_steps.append(step)
    def add_post_step(self, step: Any) -> None:
        """添加计算后置步骤"""
        self.post_steps.append(step)
    def validate_expression(self, expression: str) -> bool:
        """基础表达式合法性校验"""
        if not expression or not isinstance(expression, str):
            return False
        # 只允许数字、运算符和小数点、括号
        import re
        valid = re.match(r'^[\d\-\+\*/\.\(\)x×÷= @]+$', expression)
        return bool(valid)

    def format_result(self, result: Any) -> str:
        """统一格式化结果输出"""
        return self.fix_number_representation(result)
    """分数计算引擎"""
    
    def is_match_pattern(self, expression: str) -> bool:
        return False
    def solve(self, expression: str) -> Dict[str, Any]:
        return {
            'success': False,
            'expression': expression,
            'error': '不支持的表达式',
            'name': None,
            'result': None
        }
    def clean_expression(self, expression: str) -> str:
        """清理表达式，移除多余字符"""
        # 清理表达式，移除等号和@
        cleaned_expr = expression.replace('=@', '').replace('=', '').replace('@', '').strip()
        # 统一运算符
        cleaned_expr = cleaned_expr.replace('x', '*').replace('×', '*').replace('÷', '/')
        return cleaned_expr
    def get_operators(self, expression: str) -> list[str]:
         # 提取表达式中的运算符
        return [char for char in expression if char in operators]
    def fix_number_representation(self, expression) -> str:
        """修正数字表示法"""
        # 如果是整数，直接返回字符串形式
        if isinstance(expression, int):
            return str(expression)
        if isinstance(expression, float):
            # 保留6位精度再变成字符串
            expression = f"{expression:.6f}"
        else:
            expression = str(expression)
        # 如果有小数点，去掉小数部分的多余0
        if '.' in expression:
            expression = expression.rstrip('0').rstrip('.')
        return expression