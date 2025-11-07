"""
乘法交换结合法实现
利用乘法交换律和结合律，将容易计算的数先相乘
适用于多个数相乘，其中存在互补数（如25和4）的情况
"""

from typing import List
from ..base_types import MathCalculator, Formula, CalculationStep


class CommutativeAssociativeMultiplication(MathCalculator):
    """乘法交换结合法算法"""
    
    def __init__(self):
        super().__init__("交换结合法乘法", "重新排列乘法因子，先计算便于运算的组合", priority=5)
    
    def is_match_pattern(self, formula: Formula) -> bool:
        """匹配模式：包含互补因子的乘法表达式"""
        if formula.type != "multiplication":
            return False
        
        numbers = formula.get_numbers()
        if len(numbers) < 3:  # 至少需要3个数才有重排的意义
            return False
        
        try:
            values = [elem.get_numeric_value() for elem in numbers]
            if not all(isinstance(v, (int, float)) for v in values):
                return False
            
            # 转换为整数列表
            int_values = [int(v) for v in values]
            
            # 检查是否有有用的组合
            return self._find_useful_combinations(int_values) is not None
            
        except:
            return False
    
    def _find_useful_combinations(self, values: List[int]):
        """寻找有用的因子组合"""
        n = len(values)
        
        # 定义一些有用的组合规则
        useful_pairs = [
            (2, 5, 10), (4, 25, 100), (8, 125, 1000),
            (2, 50, 100), (4, 250, 1000), (5, 20, 100),
            (5, 2, 10), (25, 4, 100), (125, 8, 1000)
        ]
        
        # 检查两两组合
        for i in range(n):
            for j in range(i + 1, n):
                val1, val2 = values[i], values[j]
                product = val1 * val2
                
                # 检查是否是整十、整百、整千等
                if product in [10, 100, 1000] or product % 10 == 0:
                    remaining = [values[k] for k in range(n) if k != i and k != j]
                    return (i, j, val1, val2, product, remaining)
        
        # 检查三个数的组合
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    val1, val2, val3 = values[i], values[j], values[k]
                    
                    # 检查是否有两两组合后与第三个数相乘得到整数
                    pairs = [(val1, val2, val3), (val1, val3, val2), (val2, val3, val1)]
                    for pair in pairs:
                        a, b, c = pair
                        if (a * b) % 10 == 0 or (a * b) in [10, 100, 1000]:
                            remaining = [values[m] for m in range(n) if m not in [i, j, k]]
                            return (i, j, k, a, b, c, a * b, remaining)
        
        return None
    
    def construct_steps(self, formula: Formula) -> List[CalculationStep]:
        """构建交换结合法步骤"""
        numbers = formula.get_numbers()
        values = [int(elem.get_numeric_value()) for elem in numbers]
        
        # 找到有用的组合
        combination = self._find_useful_combinations(values)
        if combination is None:
            raise ValueError("No useful combination found")
        
        steps = []
        
        # 显示原始表达式
        original_expr = " × ".join(map(str, values))
        steps.append(CalculationStep(
            description=f"{original_expr} 使用交换结合法",
            operation="识别交换结合法",
            result="重新排列因子顺序"
        ))
        
        if len(combination) == 6:  # 两个数的组合
            i, j, val1, val2, product, remaining = combination
            
            steps.append(CalculationStep(
                description=f"识别有用组合：{val1} × {val2} = {product}",
                operation="识别组合",
                result=f"{val1} 和 {val2} 先相乘得到 {product}"
            ))
            
            steps.append(CalculationStep(
                description=f"先计算：{val1} × {val2} = {product}",
                operation="优先计算",
                result=product
            ))
            
            if remaining:
                remaining_expr = " × ".join(map(str, remaining))
                new_expr = f"{product} × {remaining_expr}"
                steps.append(CalculationStep(
                    description=f"重排后：{new_expr}",
                    operation="重新排列",
                    result=f"转换为 {new_expr}"
                ))
                
                # 计算最终结果
                final_result = product
                for val in remaining:
                    final_result *= val
                
                # 逐步计算剩余部分
                current_result = product
                for val in remaining:
                    new_result = current_result * val
                    steps.append(CalculationStep(
                        description=f"{current_result} × {val} = {new_result}",
                        operation="继续计算",
                        result=new_result
                    ))
                    current_result = new_result
                
                final_result = current_result
            else:
                final_result = product
        
        else:  # 三个数的组合 
            i, j, k, val1, val2, val3, intermediate, remaining = combination
            
            steps.append(CalculationStep(
                description=f"识别有用组合：{val1} × {val2} = {intermediate}",
                operation="识别组合",
                result=f"{val1} 和 {val2} 先相乘"
            ))
            
            steps.append(CalculationStep(
                description=f"先计算：{val1} × {val2} = {intermediate}",
                operation="优先计算",
                result=intermediate
            ))
            
            steps.append(CalculationStep(
                description=f"再计算：{intermediate} × {val3} = {intermediate * val3}",
                operation="继续计算",
                result=intermediate * val3
            ))
            
            current_result = intermediate * val3
            
            # 计算剩余因子
            for val in remaining:
                new_result = current_result * val
                steps.append(CalculationStep(
                    description=f"{current_result} × {val} = {new_result}",
                    operation="继续计算",
                    result=new_result
                ))
                current_result = new_result
            
            final_result = current_result
        
        steps.append(CalculationStep(
            description=f"最终结果：{final_result}",
            operation="确认结果",
            result=final_result,
            formula="交换结合法：a×b×c = (a×b)×c，优先计算便于运算的组合"
        ))
        
        return steps