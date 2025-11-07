"""
连减变加法实现
将连续减法变为减法和加法的组合
例：126 - 47 - 25 可以变为 126 - (47 + 25) 或调整为更简单的运算
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class ChainSubtractionToAddition(MathCalculator):
    """连减变加法算法"""
    
    def __init__(self):
        super().__init__("连减变加法", "将连续减法转换为加减混合运算", priority=2)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：连续减法或可优化的减法运算"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) < 3:
            return False
        
        try:
            # 检查是否全为整数
            values = [elem.get_numeric_value() for elem in numbers]
            if not all(isinstance(v, (int, float)) for v in values):
                return False
            
            # 至少要有两个数参与运算
            return len(values) >= 2
            
        except:
            return False
    
    def _find_optimization_strategy(self, minuend: float, subtrahends: List[float]) -> dict:
        """寻找最优的连减变加法策略"""
        strategies = []
        
        # 策略1：合并减数后再减
        total_subtrahend = sum(subtrahends)
        if total_subtrahend <= minuend:
            ease_score = self._calculate_ease_score(minuend, total_subtrahend)
            strategies.append({
                'type': 'combine_all',
                'description': f'先计算所有减数之和，再进行减法',
                'ease_score': ease_score,
                'operation': f'{minuend} - ({" + ".join(map(str, subtrahends))})'
            })
        
        # 策略2：寻找凑整机会
        for i, sub1 in enumerate(subtrahends):
            for j, sub2 in enumerate(subtrahends[i+1:], i+1):
                sum_pair = sub1 + sub2
                if sum_pair % 10 == 0 or sum_pair % 100 == 0:
                    remaining = [s for k, s in enumerate(subtrahends) if k != i and k != j]
                    strategies.append({
                        'type': 'pair_round',
                        'description': f'优先计算 {sub1} + {sub2} = {sum_pair}（凑整）',
                        'ease_score': 8,
                        'pair': (sub1, sub2),
                        'remaining': remaining
                    })
        
        # 策略3：寻找接近整十、整百的数进行调整
        for i, subtrahend in enumerate(subtrahends):
            # 检查是否接近整十
            rounded_10 = round(subtrahend / 10) * 10
            diff_10 = abs(subtrahend - rounded_10)
            
            if 1 <= diff_10 <= 3:
                remaining = [s for k, s in enumerate(subtrahends) if k != i]
                if subtrahend < rounded_10:  # 如 97 → 100 - 3
                    strategies.append({
                        'type': 'round_adjust',
                        'description': f'将 {subtrahend} 调整为 {rounded_10} - {diff_10}',
                        'ease_score': 7,
                        'original': subtrahend,
                        'rounded': rounded_10,
                        'adjustment': diff_10,
                        'remaining': remaining,
                        'operation': 'add_back'  # 减数变小了，要加回差值
                    })
                else:  # 如 103 → 100 + 3
                    strategies.append({
                        'type': 'round_adjust',
                        'description': f'将 {subtrahend} 调整为 {rounded_10} + {diff_10}',
                        'ease_score': 7,
                        'original': subtrahend,
                        'rounded': rounded_10,
                        'adjustment': diff_10,
                        'remaining': remaining,
                        'operation': 'subtract_more'  # 减数变大了，要多减
                    })
        
        # 如果没有找到策略，创建一个默认策略
        if not strategies:
            strategies.append({
                'type': 'sequential',
                'description': '按顺序逐步计算',
                'ease_score': 3
            })
        
        # 选择最优策略
        return max(strategies, key=lambda x: x['ease_score'])
    
    def _calculate_ease_score(self, minuend: float, subtrahend: float) -> int:
        """计算运算难易程度评分（1-10，10最容易）"""
        score = 5  # 基础分
        
        # 整十、整百加分
        if subtrahend % 100 == 0:
            score += 3
        elif subtrahend % 10 == 0:
            score += 2
        
        # 结果接近整数加分
        result = minuend - subtrahend
        if result % 100 == 0:
            score += 2
        elif result % 10 == 0:
            score += 1
        
        return min(score, 10)
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建连减变加法步骤"""
        numbers = formula.get_numbers()
        minuend = float(numbers[0].get_numeric_value())
        subtrahends = [float(num.get_numeric_value()) for num in numbers[1:]]
        
        steps = []
        
        original_expression = f"{minuend} - " + " - ".join(map(str, subtrahends))
        steps.append(CalculationStep(
            description=f"原式：{original_expression}",
            operation="识别连减运算",
            result="寻找最优的连减变加法策略"
        ))
        
        # 寻找最优策略
        strategy = self._find_optimization_strategy(minuend, subtrahends)
        
        if strategy:
            if strategy['type'] == 'combine_all':
                # 合并所有减数
                total_subtrahend = sum(subtrahends)
                steps.append(CalculationStep(
                    description=f"合并所有减数：{' + '.join(map(str, subtrahends))} = {total_subtrahend}",
                    operation="合并减数",
                    result=f"原式变为：{minuend} - {total_subtrahend}"
                ))
                
                final_result = minuend - total_subtrahend
                steps.append(CalculationStep(
                    description=f"{minuend} - {total_subtrahend} = {final_result}",
                    operation="执行减法",
                    result=final_result,
                    formula="a - b - c - ... = a - (b + c + ...)"
                ))
                
            elif strategy['type'] == 'pair_round':
                # 优先处理能凑整的一对数
                sub1, sub2 = strategy['pair']
                pair_sum = sub1 + sub2
                remaining = strategy['remaining']
                
                steps.append(CalculationStep(
                    description=f"优先计算凑整的一对：{sub1} + {sub2} = {pair_sum}",
                    operation="凑整配对",
                    result=f"原式变为：{minuend} - {pair_sum}" + (f" - {' - '.join(map(str, remaining))}" if remaining else "")
                ))
                
                intermediate_result = minuend - pair_sum
                if remaining:
                    steps.append(CalculationStep(
                        description=f"{minuend} - {pair_sum} = {intermediate_result}",
                        operation="先减凑整数",
                        result=f"继续计算：{intermediate_result} - {' - '.join(map(str, remaining))}"
                    ))
                    
                    final_result = intermediate_result - sum(remaining)
                    steps.append(CalculationStep(
                        description=f"{intermediate_result} - {sum(remaining)} = {final_result}",
                        operation="完成剩余减法",
                        result=final_result
                    ))
                else:
                    steps.append(CalculationStep(
                        description=f"最终结果：{intermediate_result}",
                        operation="完成计算",
                        result=intermediate_result,
                        formula="a - b - c = a - (b + c)，优先凑整"
                    ))
                
            elif strategy['type'] == 'round_adjust':
                # 调整接近整数的减数
                original = strategy['original']
                rounded = strategy['rounded']
                adjustment = strategy['adjustment']
                remaining = strategy['remaining']
                
                steps.append(CalculationStep(
                    description=f"调整 {original} → {rounded} {'- ' + str(adjustment) if strategy['operation'] == 'add_back' else '+ ' + str(adjustment)}",
                    operation="数值调整",
                    result=f"原式调整为便于计算的形式"
                ))
                
                if strategy['operation'] == 'add_back':
                    # 减数变小了，要加回差值
                    temp_result = minuend - rounded
                    adjusted_result = temp_result + adjustment
                    if remaining:
                        adjusted_result -= sum(remaining)
                    
                    steps.append(CalculationStep(
                        description=f"{minuend} - {rounded} + {adjustment}" + (f" - {sum(remaining)}" if remaining else "") + f" = {adjusted_result}",
                        operation="调整运算",
                        result=adjusted_result,
                        formula=f"a - {original} = a - {rounded} + {adjustment}"
                    ))
                else:
                    # 减数变大了，要多减
                    temp_result = minuend - rounded
                    adjusted_result = temp_result - adjustment
                    if remaining:
                        adjusted_result -= sum(remaining)
                    
                    steps.append(CalculationStep(
                        description=f"{minuend} - {rounded} - {adjustment}" + (f" - {sum(remaining)}" if remaining else "") + f" = {adjusted_result}",
                        operation="调整运算",
                        result=adjusted_result,
                        formula=f"a - {original} = a - {rounded} - {adjustment}"
                    ))
        
        else:
            # 没有特殊策略，直接逐步计算
            current_result = minuend
            for i, subtrahend in enumerate(subtrahends):
                new_result = current_result - subtrahend
                steps.append(CalculationStep(
                    description=f"{current_result} - {subtrahend} = {new_result}",
                    operation=f"第{i+1}次减法",
                    result=new_result
                ))
                current_result = new_result
            
            steps.append(CalculationStep(
                description=f"最终结果：{current_result}",
                operation="完成计算",
                result=current_result,
                formula="逐步减法"
            ))
        
        return steps