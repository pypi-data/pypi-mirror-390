"""
凑整/补数重写算子 - 使用凑整技巧重写表达式便于心算
"""

import re
from typing import Dict, Any, List, Tuple
from ..base_types import MixedCalculator, MixedProblem, MixedResult, MixedStep, MixedUtils


class ComplementRewritingCalculator(MixedCalculator):
    """凑整/补数重写算子"""
    
    def __init__(self):
        super().__init__("凑整重写", "使用凑整技巧重写", priority=7)

    def is_match_pattern(self, problem: MixedProblem) -> Dict[str, Any]:
        """匹配可以使用凑整技巧的表达式"""
        if problem.has_parentheses:
            return {"matched": False, "score": 0.0, "reason": "含括号表达式不适用凑整"}
        
        # 重要：只有纯加减表达式才适用凑整技巧
        # 如果包含乘除运算，应该先按运算优先级处理
        has_multiply_divide = any(op in ['*', '/'] for op in problem.operations)
        if has_multiply_divide:
            return {"matched": False, "score": 0.0, "reason": "包含乘除运算，需先按优先级处理"}
        
        # 只处理纯加减表达式的凑整
        has_add_subtract = any(op in ['+', '-'] for op in problem.operations if op not in ['(', ')'])
        if not has_add_subtract:
            return {"matched": False, "score": 0.0, "reason": "不包含加减运算"}
        
        # 检查是否有凑整机会
        complement_opportunities = self._find_complement_opportunities(problem)
        
        if complement_opportunities:
            return {
                "matched": True,
                "score": 0.6,  # 降低优先级，让混合运算算子优先处理
                "reason": f"纯加减表达式，发现{len(complement_opportunities)}个凑整机会"
            }
        
        return {"matched": False, "score": 0.0, "reason": "未发现凑整机会"}
    
    def solve(self, problem: MixedProblem) -> MixedResult:
        """执行凑整重写"""
        try:
            expression = problem.expression
            steps = []
            
            steps.append(MixedStep(
                description="识别凑整机会",
                operation="识别凑整",
                inputs=[expression],
                result="分析凑整可能",
                formula="寻找 a±b 凑整机会"
            ))
            
            # 查找凑整机会
            opportunities = self._find_complement_opportunities(problem)
            
            if not opportunities:
                return MixedResult(
                    success=False,
                    error="未找到合适的凑整机会"
                )
            
            # 应用最佳凑整策略
            best_opportunity = opportunities[0]  # 选择第一个机会
            
            rewritten_expr, rewrite_steps = self._apply_complement_rewriting(
                expression, best_opportunity
            )
            
            steps.extend(rewrite_steps)
            
            # 计算重写后的表达式
            final_result = eval(rewritten_expr)
            
            steps.append(MixedStep(
                description="计算凑整结果",
                operation="凑整计算",
                inputs=[rewritten_expr],
                result=str(final_result),
                formula=f"{rewritten_expr} = {final_result}"
            ))
            
            return MixedResult(
                success=True,
                result=final_result,
                steps=steps,
                step_count=len(steps),
                formula=f"凑整法: {expression} = {final_result}",
                validation=True,
                technique_used="凑整/补数"
            )
            
        except Exception as e:
            return MixedResult(
                success=False,
                error=f"凑整重写失败: {str(e)}"
            )

    def _apply_complement_rewriting(self, expression: str, opportunity: Dict[str, Any]):
        """应用凑整重写，支持小数，保持表达式结构"""
        steps = []
        complement = opportunity['complement']
        if opportunity['type'] == 'subtract':
            a, b = opportunity['a'], opportunity['b']
            if complement['strategy'] == 'subtract_to_ten':
                next_ten = round(complement['next_ten'], 6)
                adjustment = round(complement['adjustment'], 6)
                steps.append(MixedStep(
                    description="凑整重写",
                    operation="凑整重写",
                    inputs=[str(a), str(b)],
                    result=f"({a} - {next_ten}) + {adjustment}",
                    formula=complement['formula']
                ))
                # 用括号包裹重写部分，替换原表达式
                rewritten_expr = expression.replace(opportunity['original'], f"({a} - {next_ten}) + {adjustment}")
                return rewritten_expr, steps
        elif opportunity['type'] == 'add':
            a, b = opportunity['a'], opportunity['b']
            if complement['strategy'] == 'add_to_round':
                target = round(complement['target'], 6)
                steps.append(MixedStep(
                    description="识别凑整",
                    operation="识别凑整",
                    inputs=[str(a), str(b)],
                    result=str(target),
                    formula=f"{a} + {b} = {target}"
                ))
                rewritten_expr = expression.replace(opportunity['original'], f"({a} + {b})")
                return rewritten_expr, steps
        return expression, steps

    def _find_complement_opportunities(self, problem: MixedProblem) -> List[Dict[str, Any]]:
        """查找加减表达式中的凑整机会，支持小数"""
        expr = problem.expression
        ops = problem.operations
        opportunities = []
        # 支持整数和小数
        pattern = r'(\d+(?:\.\d+)?)\s*([\+\-])\s*(\d+(?:\.\d+)?)'
        for match in re.finditer(pattern, expr):
            a = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
            op = match.group(2)
            b = float(match.group(3)) if '.' in match.group(3) else int(match.group(3))
            original = match.group(0)
            # 检查 b 是否接近整十、整百、整千
            for base in [10, 100, 1000]:
                if op == '-':
                    next_ten = (int(b) // base + 1) * base if b % base != 0 else int(b)
                    adjustment = next_ten - b
                    if 0 < adjustment <= base / 2:
                        opportunities.append({
                            'type': 'subtract',
                            'a': a,
                            'b': b,
                            'original': original,
                            'complement': {
                                'strategy': 'subtract_to_ten',
                                'next_ten': next_ten,
                                'adjustment': adjustment,
                                'formula': f"{a} - {b} = ({a} - {next_ten}) + {adjustment}"
                            }
                        })
                elif op == '+':
                    target = a + b
                    for base2 in [10, 100, 1000]:
                        if target % base2 == 0 and base2 <= target < base2 * 10:
                            opportunities.append({
                                'type': 'add',
                                'a': a,
                                'b': b,
                                'original': original,
                                'complement': {
                                    'strategy': 'add_to_round',
                                    'target': target,
                                    'formula': f"{a} + {b} = {target}"
                                }
                            })
        return opportunities
