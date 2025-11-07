from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep, ElementType

class RevertCalculator(MathCalculator):
	def __init__(self):
		super().__init__("逆运算算子", "加减乘除逆运算求未知数", priority=2)

	def is_match_pattern(self, formula: Formula) -> bool:
		expr = formula.original_expression.replace(" ", "")  # 移除空格后再判断
		if "=" not in expr or "@" not in expr:
			return False
		eq_index = expr.index("=")
		at_index = expr.index("@")
		if at_index > eq_index:
			return False
		operators = [el.value for el in formula.elements if el.type == ElementType.OPERATOR]
		## 暂时只支持一个运算符的逆运算
		if len(operators) != 1:
			return False
		return True

	def construct_steps(self, formula: Formula) -> List[CalculationStep]:
		expr = formula.original_expression.replace(" ","")
		eq_index = expr.index("=")
		left = expr[:eq_index]
		right = expr[eq_index+1:]
		ops = ["+", "-", "×", "*", "÷", "/"]
		op = None
		# 优先匹配非*的运算符，避免与×冲突
		for o in ops:
			if o in left and (o != "*" or "×" not in left):
				op = o
				break
		if op is None:
			return [CalculationStep(description="未识别运算符", operation="错误", result="错误")]
		# 处理未知数在左侧开头的情况（@ op 数字）
		if left.startswith("@"):
			# 正确提取数字部分（支持多字符运算符后的数字）
			num_str = left.split(op, 1)[1] if op in left else left[1:]
			num_str = num_str.strip('+-*×÷')
			try:
				num = float(num_str)
				right_val = float(right)
			except:
				return [CalculationStep(description="数字解析失败", operation="错误", result="错误")]
			if op == "+":
				x = right_val - num
				steps = [
					CalculationStep(description=f"设未知数为x，x+{num}={right_val}", operation="逆加法", result=f"x={right_val}-{num}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			elif op == "-":
				x = right_val + num
				steps = [
					CalculationStep(description=f"设未知数为x，x-{num}={right_val}", operation="逆减法", result=f"x={right_val}+{num}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			elif op == "*" or op == "×":
				x = right_val / num
				steps = [
					CalculationStep(description=f"设未知数为x，x×{num}={right_val}", operation="逆乘法", result=f"x={right_val}÷{num}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			elif op == "÷":
				x = right_val * num
				steps = [
					CalculationStep(description=f"设未知数为x，x÷{num}={right_val}", operation="逆除法", result=f"x={right_val}×{num}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			else:
				steps = [CalculationStep(description="不支持的运算符", operation="错误", result="错误")]
			return steps
		else:
			# 处理数字 op 未知数的情况
			parts = left.split(op, 1)  # 只分割一次，避免数字中包含运算符
			if len(parts) != 2:
				return [CalculationStep(description="表达式格式错误", operation="错误", result="错误")]
			num_str, unknown_str = parts[0], parts[1]
			num_str = num_str.strip('+-*×÷')
			# 验证未知数格式
			if unknown_str.strip() != "@":
				return [CalculationStep(description="表达式格式错误", operation="错误", result="错误")]
			try:
				num = float(num_str)
				right_val = float(right)
			except:
				return [CalculationStep(description="数字解析失败", operation="错误", result="错误")]
			if op == "+":
				x = right_val - num
				steps = [
					CalculationStep(description=f"设未知数为x，{num}+x={right_val}", operation="逆加法", result=f"x={right_val}-{num}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			elif op == "-":
				x = num - right_val
				steps = [
					CalculationStep(description=f"设未知数为x，{num}-x={right_val}", operation="逆减法", result=f"x={num}-{right_val}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			elif op == "*"  or op == "×":
				x = right_val / num
				steps = [
					CalculationStep(description=f"设未知数为x，{num}×x={right_val}", operation="逆乘法", result=f"x={right_val}÷{num}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			elif op == "÷":
				x = num / right_val
				steps = [
					CalculationStep(description=f"设未知数为x，{num}÷x={right_val}", operation="逆除法", result=f"x={num}÷{right_val}"),
					CalculationStep(description="计算x", operation="计算", result=x)
				]
			else:
				steps = [CalculationStep(description="不支持的运算符", operation="错误", result="错误")]
			return steps