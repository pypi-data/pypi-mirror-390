import itertools
from typing import List, Tuple, Dict, Any, Optional

# ================== 1. 核心数据结构 ==================

class Node:
    """表达式树节点，用于构建AST"""
    def __init__(self, value: Any, left: Optional['Node'] = None, right: Optional['Node'] = None, op: Optional[str] = None):
        self.value = value  # 如果是叶子节点，则为数字；否则为操作符
        self.left = left
        self.right = right
        self.op = op
        
        # 用于存储优化信息
        self.strategy_name: Optional[str] = None
        self.strategy_score: int = 0
        self.result: Optional[float] = None

    def is_leaf(self) -> bool:
        """判断是否为叶子节点（即数字）"""
        return self.op is None

    def __repr__(self) -> str:
        """方便调试，打印表达式树"""
        if self.is_leaf():
            return str(self.value)
        return f"({self.left} {self.op} {self.right})"

# ================== 2. 策略库 ==================

class StrategyLibrary:
    """管理所有混合运算速算策略"""
    def __init__(self):
        self.strategies = [
            {"name": "凑整成百", "op": ['+', '-'], "level": "高", "score": 5, "func": self.is_round_to_100},
            {"name": "凑整成十", "op": ['+', '-'], "level": "高", "score": 4, "func": self.is_round_to_10},
            {"name": "小数凑整", "op": ['+'], "level": "中", "score": 2, "func": self.is_decimal_to_integer},
            {"name": "提取公因数", "op": ['*'], "level": "高", "score": 4, "func": self.can_extract_common_factor},
            {"name": "补数法", "op": ['+', '-'], "level": "中", "score": 3, "func": self.is_complementary},
            {"name": "倍数简化", "op": ['/'], "level": "中", "score": 3, "func": self.is_multiple_simplification},
        ]

    def get_best_strategy(self, node: Node) -> Optional[Dict]:
        """为给定的二元运算节点找到最佳策略"""
        if node.is_leaf() or not node.left or not node.right or not node.left.is_leaf() or not node.right.is_leaf():
            return None

        best_strategy = None
        for strategy in self.strategies:
            if node.op in strategy["op"] and strategy["func"](node.left.value, node.right.value):
                if not best_strategy or strategy["score"] > best_strategy["score"]:
                    best_strategy = strategy
        return best_strategy

    # --- 策略的具体实现 ---
    def is_round_to_100(self, a: float, b: float) -> bool:
        return (a + b) % 100 == 0

    def is_round_to_10(self, a: float, b: float) -> bool:
        return (a + b) % 10 == 0

    def is_decimal_to_integer(self, a: float, b: float) -> bool:
        """判断两个数（至少一个为小数）相加是否凑成整数"""
        # 检查至少一个数是小数
        a_is_decimal = isinstance(a, float) and not a.is_integer()
        b_is_decimal = isinstance(b, float) and not b.is_integer()
        if not (a_is_decimal or b_is_decimal):
            return False
        # 检查相加结果是否为整数
        result = a + b
        return isinstance(result, float) and result.is_integer()

    def can_extract_common_factor(self, a: float, b: float) -> bool:
        # 这是一个简化的例子，实际需要更复杂的树结构分析
        return False 

    def is_complementary(self, a: float, b: float) -> bool:
        return abs(a % 10 + b % 10 - 10) < 1e-9 or abs(a % 100 + b % 100 - 100) < 1e-9

    def is_multiple_simplification(self, a: float, b: float) -> bool:
        return b != 0 and a % b == 0

# ================== 3. 表达式优化器 ==================

class ExpressionOptimizer:
    """混合运算优化器，负责寻找最佳计算路径"""
    def __init__(self):
        self.strategy_lib = StrategyLibrary()

    def _parse_expression_with_structure(self, expr: str) -> dict:
        """解析表达式，保持结构信息以便进行高级优化"""
        import re
        
        # 移除空格
        expr = expr.replace(" ", "")
        
        # 使用正则表达式分割表达式，保留运算符
        tokens = re.split(r'([+\-*/])', expr)
        tokens = [token for token in tokens if token]  # 移除空字符串
        
        # 处理负数开头的情况
        if tokens and tokens[0] == '-':
            tokens = ['-' + tokens[1]] + tokens[2:]
        
        # 分析表达式结构，寻找优化模式
        optimization_found = self._find_optimization_patterns(tokens)
        
        if optimization_found:
            return optimization_found
        
        # 如果没有找到特殊优化模式，按常规方式处理
        return self._parse_conventional(tokens)
    
    def _find_optimization_patterns(self, tokens: List[str]) -> Optional[dict]:
        """寻找特殊的优化模式，如提取公因数等"""
        
        # 模式1: 提取公因数 (a*c + b*c = (a+b)*c)
        multiplication_terms = []
        addition_terms = []
        
        i = 0
        current_sign = 1
        
        while i < len(tokens):
            if tokens[i] in ['+', '-']:
                current_sign = 1 if tokens[i] == '+' else -1
                i += 1
                continue
            
            # 检查是否是乘法项
            if i + 2 < len(tokens) and tokens[i + 1] == '*':
                left = float(tokens[i])
                right = float(tokens[i + 2])
                multiplication_terms.append({
                    'left': left * current_sign,
                    'right': right,
                    'sign': current_sign
                })
                i += 3
            else:
                # 普通数字
                addition_terms.append(float(tokens[i]) * current_sign)
                i += 1
            
            current_sign = 1  # 重置符号
        
        # 检查是否有公因数
        if len(multiplication_terms) >= 2:
            common_factors = self._find_common_factors(multiplication_terms)
            if common_factors:
                return {
                    'type': 'common_factor',
                    'terms': multiplication_terms,
                    'addition_terms': addition_terms,
                    'common_factors': common_factors
                }
        
        return None
    
    def _find_common_factors(self, terms: List[dict]) -> Optional[dict]:
        """寻找乘法项中的公因数"""
        if len(terms) < 2:
            return None
            
        # 检查right部分是否有公因数
        right_values = [term['right'] for term in terms]
        if len(set(right_values)) == 1:  # 所有right值相同
            factor = right_values[0]
            coefficients = [term['left'] for term in terms]
            return {
                'factor': factor,
                'coefficients': coefficients,
                'position': 'right'
            }
        
        # 检查left部分是否有公因数
        left_values = [term['left'] for term in terms]
        if len(set(left_values)) == 1:  # 所有left值相同
            factor = left_values[0]
            coefficients = [term['right'] for term in terms]
            return {
                'factor': factor,
                'coefficients': coefficients,
                'position': 'left'
            }
        
        return None
    
    def _parse_conventional(self, tokens: List[str]) -> dict:
        """常规解析方式，先计算乘除法"""
        # 先计算所有乘除法
        i = 1  # 从第一个运算符开始
        while i < len(tokens):
            if i < len(tokens) and tokens[i] in ['*', '/']:
                left_val = float(tokens[i-1])
                operator = tokens[i]
                right_val = float(tokens[i+1])
                
                if operator == '*':
                    result = left_val * right_val
                else:  # operator == '/'
                    result = left_val / right_val
                
                # 替换这三个token为计算结果
                tokens = tokens[:i-1] + [str(result)] + tokens[i+2:]
            else:
                i += 2  # 跳过操作数和运算符
        
        # 处理加减法
        result_numbers = []
        current_sign = 1
        
        for i, token in enumerate(tokens):
            if token in ['+', '-']:
                current_sign = 1 if token == '+' else -1
            else:
                try:
                    num = float(token)
                    if i == 0:
                        result_numbers.append(num)
                    else:
                        result_numbers.append(current_sign * num)
                except ValueError:
                    continue
        
        return {
            'type': 'conventional',
            'numbers': result_numbers
        }

    def _build_tree_from_sequence(self, seq: List[float], op: str) -> Node:
        """从一个数字序列构建一个左深树"""
        if not seq:
            return Node(0)
        
        tree = Node(seq[0])
        for i in range(1, len(seq)):
            tree = Node(op, left=tree, right=Node(seq[i]), op=op)
        return tree

    def _evaluate_tree(self, node: Optional[Node]) -> Tuple[Optional[float], int]:
        """评估一棵表达式树的总奖励分数"""
        if not node:
            return 0.0, 0
        if node.is_leaf():
            return node.value, 0
        
        left_val, left_score = self._evaluate_tree(node.left)
        right_val, right_score = self._evaluate_tree(node.right)
        
        total_score = left_score + right_score
        
        # 计算当前节点结果
        if left_val is not None and right_val is not None:
            if node.op == '+':
                node.result = left_val + right_val
            elif node.op == '-':
                node.result = left_val - right_val
            # ...可以扩展其他操作符
        
        # 检查当前节点是否能应用策略
        strategy = self.strategy_lib.get_best_strategy(node)
        if strategy:
            node.strategy_name = strategy["name"]
            node.strategy_score = strategy["score"]
            total_score += strategy["score"]
            
        return node.result, total_score

    def _generate_associative_trees(self, numbers: Tuple[float, ...], op: str) -> List[Node]:
        """
        应用结合律，通过递归和缓存生成给定数字序列所有可能的二叉树结构。
        """
        if not numbers:
            return []
        if len(numbers) == 1:
            return [Node(numbers[0])]
        
        # 检查缓存
        if (numbers, op) in self.tree_cache:
            return self.tree_cache[(numbers, op)]

        all_trees = []
        # i 代表切分点，将 numbers 分为 left_part 和 right_part
        for i in range(1, len(numbers)):
            left_part = numbers[:i]
            right_part = numbers[i:]
            
            left_trees = self._generate_associative_trees(left_part, op)
            right_trees = self._generate_associative_trees(right_part, op)
            
            for l_tree in left_trees:
                for r_tree in right_trees:
                    all_trees.append(Node(op, left=l_tree, right=r_tree, op=op))
        
        # 存入缓存
        self.tree_cache[(numbers, op)] = all_trees
        return all_trees

    def _generate_candidates(self, numbers: List[float], op: str) -> List[Node]:
        """应用交换律和结合律生成所有可能的计算树"""
        self.tree_cache: Dict[Tuple, List[Node]] = {} # 为每次调用清空缓存
        candidates = []
        # 1. 应用交换律：生成所有排列
        # 为了减少计算量，对于大于6个数的排列，我们只取一部分样本
        num_perms = list(itertools.permutations(numbers))
        if len(numbers) > 6:
            num_perms = num_perms[:100] # 限制排列数量

        for perm in num_perms:
            # 2. 应用结合律：为每种排列生成所有可能的二叉树结构
            candidates.extend(self._generate_associative_trees(perm, op))
        
        # 去重，因为不同排列可能产生相同的树结构
        unique_candidates = []
        seen_trees = set()
        for tree in candidates:
            tree_repr = repr(tree)
            if tree_repr not in seen_trees:
                unique_candidates.append(tree)
                seen_trees.add(tree_repr)
        
        return unique_candidates


    def _generate_steps(self, node: Optional[Node]) -> List[str]:
        """从优化后的树生成人类可读的步骤"""
        if not node or node.is_leaf():
            return []
        
        # 深度优先遍历，后序生成步骤
        steps = self._generate_steps(node.left) + self._generate_steps(node.right)
        
        step_desc = f"{node.left} {node.op} {node.right} = {node.result}"
        if node.strategy_name:
            step_desc += f"  【{node.strategy_name}，+{node.strategy_score}分】"
        
        steps.append(step_desc)
        return steps

    def _collect_strategies(self, node: Optional[Node]) -> List[dict]:
        """收集树中所有使用的策略"""
        if not node:
            return []
        
        strategies = []
        
        # 收集左右子树的策略
        strategies.extend(self._collect_strategies(node.left))
        strategies.extend(self._collect_strategies(node.right))
        
        # 收集当前节点的策略
        if node.strategy_name:
            strategies.append({
                'name': node.strategy_name,
                'score': node.strategy_score,
                'description': f"{node.left} {node.op} {node.right} = {node.result}"
            })
        
        return strategies

    def optimize(self, expr: str):
        """主流程：解析、优化、评估并输出结果"""
        print(f"\n{'='*80}")
        print(f"                    小学数学速算 - 混合运算优化")
        print(f"{'='*80}")
        
        # 第1步：展示待计算问题算式
        print(f"📝 第一步：原始算式")
        print(f"   待计算表达式：{expr}")
        print()
        
        # 1. 解析表达式，识别优化模式
        parsed_result = self._parse_expression_with_structure(expr)
        
        if parsed_result['type'] == 'common_factor':
            # 处理公因数优化
            self._optimize_common_factor(expr, parsed_result)
        else:
            # 常规优化流程
            self._optimize_conventional(expr, parsed_result['numbers'])
    
    def _optimize_common_factor(self, expr: str, parsed_result: dict):
        """处理公因数优化"""
        common_factors = parsed_result['common_factors']
        terms = parsed_result['terms']
        addition_terms = parsed_result['addition_terms']
        
        factor = common_factors['factor']
        coefficients = common_factors['coefficients']
        
        # 第2步：优化后的算式，并解释优化点
        print(f"🎯 第二步：优化策略识别")
        print(f"   策略名称：提取公因数优化")
        print(f"   识别公因数：{factor}")
        print(f"   系数列表：{coefficients}")
        
        # 构建优化后的表达式
        coefficients_str = ' + '.join([str(c) if c >= 0 else f'({c})' for c in coefficients])
        optimized_expr = f"({coefficients_str}) × {factor}"
        if addition_terms:
            other_sum = sum(addition_terms)
            if other_sum >= 0:
                optimized_expr += f" + {other_sum}"
            else:
                optimized_expr += f" + ({other_sum})"
                
        print(f"   优化后算式：{optimized_expr}")
        print(f"   优化说明：将相同因数 {factor} 提取出来，简化乘法运算")
        print()
        
        # 第3步：展示对优化后算式的逐步计算结果
        print(f"🧮 第三步：逐步计算过程")
        
        # 计算系数和
        coeff_sum = sum(coefficients)
        print(f"   步骤1：计算系数和")
        coeffs_calculation = ' + '.join([str(c) if c >= 0 else f'({c})' for c in coefficients])
        print(f"          {coeffs_calculation} = {coeff_sum}")
        
        # 计算主要结果
        factored_result = coeff_sum * factor
        print(f"   步骤2：系数和乘以公因数")
        print(f"          {coeff_sum} × {factor} = {factored_result}")
        
        # 处理其他加法项
        final_result = factored_result
        if addition_terms:
            other_sum = sum(addition_terms)
            print(f"   步骤3：加上其他项")
            if other_sum >= 0:
                print(f"          {factored_result} + {other_sum} = {factored_result + other_sum}")
            else:
                print(f"          {factored_result} + ({other_sum}) = {factored_result + other_sum}")
            final_result = factored_result + other_sum
        
        print(f"   最终结果：{final_result}")
        print()
        
        # 第4步：评估与检查结果
        print(f"✅ 第四步：结果验证")
        try:
            standard_result = eval(expr)
        except:
            standard_result = final_result
            
        print(f"   原始算式计算：{expr} = {standard_result}")
        print(f"   优化算式计算：{optimized_expr} = {final_result}")
        print(f"   结果对比：{'✅ 正确' if abs(standard_result - final_result) < 1e-9 else '❌ 错误'}")
        
        # 计算节省的运算步骤
        original_ops = len([c for c in expr if c in '+-*/'])
        optimized_ops = len(coefficients) - 1 + 1 + (1 if addition_terms else 0)  # 系数相加 + 一次乘法 + 可能的加法
        saved_ops = original_ops - optimized_ops
        if saved_ops > 0:
            print(f"   效率提升：节省了 {saved_ops} 步运算")
        print()
        
        if abs(standard_result - final_result) < 1e-9:
            print("🎉 优化成功！算法正确应用了提取公因数策略。")
        else:
            print("❌ 优化失败！结果不匹配，请检查算法。")
    
    def _optimize_conventional(self, expr: str, numbers: List[float]):
        """常规优化流程"""
        op = '+'
        
        # 第2步开始：展示解析结果
        print(f"🔍 解析识别：数字列表 {numbers}")
        print()

        # 2. 生成所有候选计算路径（二叉树）
        candidate_trees = self._generate_candidates(numbers, op)

        # 3. 评估并选择最优方案
        best_tree = None
        max_score = -1
        all_strategies = []

        for tree in candidate_trees:
            _, score = self._evaluate_tree(tree)
            strategies = self._collect_strategies(tree)
            all_strategies.extend(strategies)
            if score > max_score:
                max_score = score
                best_tree = tree
        
        # 如果没有找到优化策略，使用原始顺序
        if not best_tree:
            best_tree = self._build_tree_from_sequence(numbers, op)
        
        # 重新评估最优树以填充结果
        self._evaluate_tree(best_tree)

        # 第2步：优化后的算式，并解释优化点
        print(f"🎯 第二步：优化策略识别")
        used_strategies = self._collect_strategies(best_tree)
        if used_strategies:
            print(f"   发现优化策略：")
            for strategy in used_strategies:
                print(f"     • {strategy['name']} (奖励分数: +{strategy['score']})")
                print(f"       应用位置: {strategy['description']}")
            print(f"   总优化得分：{max_score} 分")
        else:
            print(f"   未发现特殊优化策略，使用常规计算顺序")
            print(f"   总得分：{max_score} 分")
            
        print(f"   优化后算式：{best_tree}")
        print()

        # 第3步：展示对优化后算式的逐步计算结果  
        print(f"🧮 第三步：逐步计算过程")
        steps = self._generate_steps(best_tree)
        for i, step in enumerate(steps, 1):
            print(f"   步骤{i}：{step}")
        print(f"   最终结果：{best_tree.result}")
        print()

        # 第4步：评估与检查结果
        print(f"✅ 第四步：结果验证")
        try:
            standard_result = eval(expr)
        except:
            standard_result = sum(numbers)
            
        optimized_result = best_tree.result
        
        print(f"   原始算式计算：{expr} = {standard_result}")
        print(f"   优化算式计算：{best_tree} = {optimized_result}")
        print(f"   结果对比：{'✅ 正确' if optimized_result is not None and abs(standard_result - optimized_result) < 1e-9 else '❌ 错误'}")
        
        # 显示优化效果
        if max_score > 0:
            print(f"   优化效果：应用了 {len(used_strategies)} 个优化策略，总得分 {max_score} 分")
        else:
            print(f"   优化效果：未发现明显的优化机会")
        print()

        if optimized_result is None or abs(standard_result - optimized_result) > 1e-9:
            print("❌ 优化失败！结果不匹配或计算错误。")
        else:
            print("🎉 优化成功！算法正确应用了速算策略。")


