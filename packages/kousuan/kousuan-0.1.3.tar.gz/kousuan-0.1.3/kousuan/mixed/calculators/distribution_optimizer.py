"""
分配律优化算子 - 使用分配律简化含括号的乘法运算
"""

import re
from typing import Dict, Any
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep


class DistributionOptimizer(MixedCalculator):
    """分配律优化算子"""
    
    def __init__(self):
        super().__init__("分配律优化", "使用分配律简化乘法与括号运算", priority=6)
    
    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配可以使用分配律的表达式"""
        if not problem.has_parentheses:
            return {"matched": False, "score": 0.0, "reason": "无括号不需要分配律"}
        
        # 查找 a*(b+c) 或 (b+c)*a 的模式
        expr = problem.expression
        
        # 匹配模式: 数字 * (表达式) 或 (表达式) * 数字
        pattern1 = r'(\d+(?:\.\d+)?)\s*\*\s*\(([^()]+)\)'  # a*(b+c)
        pattern2 = r'\(([^()]+)\)\s*\*\s*(\d+(?:\.\d+)?)'  # (b+c)*a
        
        # 检查第一种模式: a*(b+c)
        match1 = re.search(pattern1, expr)
        if match1:
            try:
                multiplier = float(match1.group(1))
                bracket_content = match1.group(2)
                
                # 检查是否值得使用分配律（如果乘数是10、100、2、5等特殊数）
                if multiplier in [2, 5, 10, 25, 50, 100, 0.5, 0.1, 0.25]:
                    return {
                        "matched": True,
                        "score": 0.9,
                        "reason": f"可使用分配律优化，乘数为{multiplier}"
                    }
                else:
                    return {
                        "matched": True,
                        "score": 0.6,
                        "reason": "可使用分配律，但优势不明显"
                    }
            except ValueError:
                pass
        
        # 检查第二种模式: (b+c)*a
        match2 = re.search(pattern2, expr)
        if match2:
            try:
                multiplier = float(match2.group(2))
                bracket_content = match2.group(1)
                
                # 检查是否值得使用分配律
                if multiplier in [2, 5, 10, 25, 50, 100, 0.5, 0.1, 0.25]:
                    return {
                        "matched": True,
                        "score": 0.9,
                        "reason": f"可使用分配律优化，乘数为{multiplier}"
                    }
                else:
                    return {
                        "matched": True,
                        "score": 0.6,
                        "reason": "可使用分配律，但优势不明显"
                    }
            except ValueError:
                pass
        
        return {"matched": False, "score": 0.0, "reason": "未找到分配律优化机会"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行分配律优化"""
        try:
            expression = problem.expression
            steps = []
            
            steps.append(MixedStep(
                description="识别分配律模式",
                operation="识别分配律",
                inputs=[expression],
                result="分配律适用",
                formula="a×(b+c) = a×b + a×c"
            ))
            
            # 查找并应用分配律
            result_expr, distribution_steps = self._apply_distribution_law(expression)
            
            steps.extend(distribution_steps)
            
            # 计算最终结果
            final_result = eval(result_expr)
            
            steps.append(MixedStep(
                description="分配律展开完成",
                operation="展开完成",
                inputs=[result_expr],
                result=str(final_result),
                formula=f"{result_expr} = {final_result}"
            ))
            
            return MixedResult(
                success=True,
                result=final_result,
                steps=steps,
                step_count=len(steps),
                formula=f"分配律: {expression} = {final_result}",
                validation=True,
                technique_used="分配律"
            )
            
        except Exception as e:
            return MixedResult(
                success=False,
                error=f"分配律优化失败: {str(e)}"
            )

    def _apply_distribution_law(self, expression: str):
        """应用分配律"""
        steps = []
        
        # 匹配 a*(b+c) 模式
        pattern1 = r'(\d+(?:\.\d+)?)\s*\*\s*\(([^()]+)\)'
        match1 = re.search(pattern1, expression)
        
        if match1:
            multiplier = match1.group(1)
            bracket_content = match1.group(2)
            
            steps.append(MixedStep(
                description="识别分配模式",
                operation="识别模式",
                inputs=[multiplier, bracket_content],
                result=f"分配律模式",
                formula=f"{multiplier} × ({bracket_content})"
            ))
            
            # 解析括号内的表达式
            terms = self._parse_bracket_terms(bracket_content)
            
            # 应用分配律
            distributed_terms = []
            for term in terms:
                distributed = f"{multiplier}×{term}"
                distributed_terms.append(distributed)
            
            distributed_expr = " + ".join(distributed_terms)
            
            steps.append(MixedStep(
                description="应用分配律",
                operation="应用分配律",
                inputs=[multiplier, bracket_content],
                result=distributed_expr,
                formula=f"分配律展开: {distributed_expr}"
            ))
            
            # 计算每项
            calculated_terms = []
            for i, term in enumerate(terms):
                try:
                    calc_result = eval(f"{multiplier}*{term}")
                    calculated_terms.append(str(calc_result))
                    
                    steps.append(MixedStep(
                        description="计算分配项",
                        operation="计算分配项",
                        inputs=[multiplier, term],
                        result=str(calc_result),
                        formula=f"{multiplier} × {term} = {calc_result}"
                    ))
                except:
                    # 如果计算失败，保持原样
                    calculated_terms.append(f"{multiplier}*{term}")
            
            final_expr = " + ".join(calculated_terms)
            
            # 替换原表达式中的部分
            result_expr = expression.replace(match1.group(0), f"({final_expr})")
            
            return result_expr, steps
        
        # 匹配 (b+c)*a 模式
        pattern2 = r'\(([^()]+)\)\s*\*\s*(\d+(?:\.\d+)?)'
        match2 = re.search(pattern2, expression)
        
        if match2:
            bracket_content = match2.group(1)
            multiplier = match2.group(2)
            
            steps.append(MixedStep(
                description=f"识别模式: ({bracket_content}) × {multiplier}",
                operation="identify_pattern",
                inputs=[bracket_content, multiplier],
                result=f"分配律模式",
                formula=f"({bracket_content}) × {multiplier}"
            ))
            
            terms = self._parse_bracket_terms(bracket_content)
            distributed_terms = [f"{term}*{multiplier}" for term in terms]
            distributed_expr = " + ".join(distributed_terms)
            
            steps.append(MixedStep(
                description="应用分配律",
                operation="应用分配律",
                inputs=[bracket_content, multiplier],
                result=distributed_expr,
                formula=f"分配律展开: {distributed_expr}"
            ))
            
            calculated_terms = []
            for term in terms:
                try:
                    calc_result = eval(f"{term}*{multiplier}")
                    calculated_terms.append(str(calc_result))
                except:
                    calculated_terms.append(f"{term}*{multiplier}")
            
            final_expr = " + ".join(calculated_terms)
            result_expr = expression.replace(match2.group(0), f"({final_expr})")
            
            return result_expr, steps
        
        return expression, steps
    
    def _parse_bracket_terms(self, bracket_content: str):
        """解析括号内的项"""
        # 简单的加减项解析
        terms = []
        current_term = ""
        sign = 1
        
        i = 0
        while i < len(bracket_content):
            char = bracket_content[i]
            
            if char in ['+', '-']:
                if current_term:
                    terms.append(current_term.strip())
                    current_term = ""
                if char == '-':
                    current_term = "-"
            else:
                current_term += char
            i += 1
        
        if current_term:
            terms.append(current_term.strip())
        
        return terms
