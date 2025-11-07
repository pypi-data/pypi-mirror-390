"""
反用加法实现
将减法转换为加法来计算，特别适用于被减数小于减数的情况
或者通过添加相同数值来简化计算
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class InverseAdditionSubtraction(MathCalculator):
    """反用加法算法"""
    
    def __init__(self):
        super().__init__("反用加法", "将减法转换为加法计算", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：适合转换为加法的减法运算"""
        if formula.type != "subtraction":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) != 2:
            return False
        
        try:
            values = [elem.get_numeric_value() for elem in numbers]
            if not all(isinstance(v, (int, float)) for v in values):
                return False
            
            minuend, subtrahend = values
            
            # 情况1：被减数小于减数（结果为负）
            if minuend < subtrahend:
                return True
            
            # 情况2：通过加法验算更简单
            # 检查是否存在便于加法计算的数值关系
            diff = minuend - subtrahend
            if diff > 0:
                # 如果差值较小且容易通过加法验证
                if diff < min(minuend, subtrahend) / 2:
                    return True
                    
                # 如果减数接近某个整数倍关系
                for base in [10, 100, 1000]:
                    if abs(subtrahend % base) <= 3 or abs(base - (subtrahend % base)) <= 3:
                        return True
            
            return False
            
        except:
            return False
    
    def _find_addition_strategy(self, minuend: float, subtrahend: float) -> dict:
        """寻找最适合的反用加法策略"""
        strategies = []
        
        # 策略1：直接转换（当被减数小于减数时）
        if minuend < subtrahend:
            strategies.append({
                'type': 'negative_result',
                'description': f'被减数小于减数，结果为负数',
                'calculation': f'{subtrahend} - {minuend} = {subtrahend - minuend}',
                'final_result': minuend - subtrahend,
                'ease_score': 9
            })
        
        # 策略2：加法验算法
        result = minuend - subtrahend
        if result > 0:
            strategies.append({
                'type': 'addition_check',
                'description': f'用加法验算：{subtrahend} + ? = {minuend}',
                'calculation': f'{subtrahend} + {result} = {minuend}',
                'result': result,
                'ease_score': 7
            })
        
        # 策略3：补数加法
        # 寻找接近整数倍的补数
        for base in [10, 100, 1000]:
            if subtrahend < base:
                complement = base - subtrahend
                if 1 <= complement <= base // 10:  # 补数不能太大
                    adjusted_minuend = minuend + complement
                    strategies.append({
                        'type': 'complement_addition',
                        'description': f'补数法：将 {subtrahend} 补至 {base}',
                        'complement': complement,
                        'base': base,
                        'adjusted_minuend': adjusted_minuend,
                        'calculation': f'({minuend} + {complement}) - {base} = {adjusted_minuend} - {base} = {adjusted_minuend - base}',
                        'result': adjusted_minuend - base,
                        'ease_score': 8 if base == 10 else 6
                    })
        
        # 策略4：分解加法
        # 将减数分解为更容易的加法组合
        if subtrahend >= 10:
            # 尝试分解为整十数和个位数
            tens = (int(subtrahend) // 10) * 10
            ones = int(subtrahend) % 10
            
            if ones != 0 and tens != 0:
                temp_result = minuend - tens
                final_result = temp_result - ones
                strategies.append({
                    'type': 'decompose_subtraction',
                    'description': f'分解减数：{subtrahend} = {tens} + {ones}',
                    'tens': tens,
                    'ones': ones,
                    'temp_result': temp_result,
                    'calculation': f'{minuend} - {tens} - {ones} = {temp_result} - {ones} = {final_result}',
                    'result': final_result,
                    'ease_score': 6
                })
        
        # 如果没有特殊策略，使用基本加法验算
        if not strategies:
            result = minuend - subtrahend
            strategies.append({
                'type': 'basic_check',
                'description': '基本加法验算',
                'calculation': f'{subtrahend} + {result} = {minuend}',
                'result': result,
                'ease_score': 5
            })
        
        return max(strategies, key=lambda x: x['ease_score'])
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建反用加法步骤"""
        numbers = formula.get_numbers()
        minuend = float(numbers[0].get_numeric_value())
        subtrahend = float(numbers[1].get_numeric_value())
        
        steps = []
        
        steps.append(CalculationStep(
            description=f"{minuend} - {subtrahend} 使用反用加法",
            operation="识别减法转加法",
            result="寻找最适合的加法转换策略"
        ))
        
        strategy = self._find_addition_strategy(minuend, subtrahend)
        
        if strategy['type'] == 'negative_result':
            steps.append(CalculationStep(
                description=f"被减数 {minuend} < 减数 {subtrahend}，结果为负数",
                operation="识别负数结果",
                result="转换为：-（减数 - 被减数）"
            ))
            
            positive_diff = subtrahend - minuend
            steps.append(CalculationStep(
                description=f"计算：{subtrahend} - {minuend} = {positive_diff}",
                operation="计算正差值",
                result=positive_diff
            ))
            
            steps.append(CalculationStep(
                description=f"最终结果：-{positive_diff} = {strategy['final_result']}",
                operation="添加负号",
                result=strategy['final_result'],
                formula="a - b = -(b - a) 当 a < b 时"
            ))
            
        elif strategy['type'] == 'addition_check':
            steps.append(CalculationStep(
                description=f"用加法验算：{subtrahend} + ? = {minuend}",
                operation="加法验算设置",
                result=f"寻找使等式成立的数值"
            ))
            
            result = strategy['result']
            steps.append(CalculationStep(
                description=f"验算：{subtrahend} + {result} = {minuend}",
                operation="加法验算",
                result=f"所以 {minuend} - {subtrahend} = {result}"
            ))
            
            steps.append(CalculationStep(
                description=f"最终结果：{result}",
                operation="确认结果",
                result=result,
                formula="减法验算：a - b = c ⟺ b + c = a"
            ))
            
        elif strategy['type'] == 'complement_addition':
            complement = strategy['complement']
            base = strategy['base']
            adjusted_minuend = strategy['adjusted_minuend']
            
            steps.append(CalculationStep(
                description=f"补数法：将 {subtrahend} 补至 {base}，需要加 {complement}",
                operation="确定补数",
                result=f"同时给被减数和减数都加 {complement}"
            ))
            
            steps.append(CalculationStep(
                description=f"调整后：({minuend} + {complement}) - ({subtrahend} + {complement}) = {adjusted_minuend} - {base}",
                operation="补数调整",
                result=f"{adjusted_minuend} - {base}"
            ))
            
            final_result = adjusted_minuend - base
            steps.append(CalculationStep(
                description=f"{adjusted_minuend} - {base} = {final_result}",
                operation="计算结果",
                result=final_result,
                formula=f"补数法：(a+k) - (b+k) = a - b"
            ))
            
        elif strategy['type'] == 'decompose_subtraction':
            tens = strategy['tens']
            ones = strategy['ones']
            temp_result = strategy['temp_result']
            
            steps.append(CalculationStep(
                description=f"分解减数：{subtrahend} = {tens} + {ones}",
                operation="减数分解",
                result=f"分步计算：先减 {tens}，再减 {ones}"
            ))
            
            steps.append(CalculationStep(
                description=f"第一步：{minuend} - {tens} = {temp_result}",
                operation="减去整十数",
                result=temp_result
            ))
            
            final_result = temp_result - ones
            steps.append(CalculationStep(
                description=f"第二步：{temp_result} - {ones} = {final_result}",
                operation="减去个位数",
                result=final_result,
                formula="分解减法：a - (b + c) = a - b - c"
            ))
            
        else:
            # 基本加法验算
            result = strategy['result']
            steps.append(CalculationStep(
                description=f"基本验算：{subtrahend} + {result} = {minuend}",
                operation="加法验算",
                result=result,
                formula="减法验算：a - b = c ⟺ b + c = a"
            ))
        
        return steps