**面向工程化、可注册算子（operator）框架**的完整设计方案，专注于 **加减乘除混合运算**（含括号、无括号、特殊数 0/1、凑整/补数等心算技巧）。文档包含：

* 题型归类（可直接作为分类器模板）
* 解题技巧汇总（用于算子内部与执行规划器）
* 针对每类题型的**算子列表**（名称、匹配规则/模板、分步骤解题分析）——可直接变成 `operator_registry` 的元数据
* 算子体系架构与执行流程（接口契约、Planner/Executor/Validator 分工）
* 错误/特殊情形处理、测试与验证建议

全部以 Markdown 列表 + 规范化描述给出，便于直接导入你现有工程或作为 PR 文档。

---

# 1 题型汇总（一级分类）

按表达式结构与运算元素，将题型分为：

1. 纯一元运算（基础，直接由解析器识别）

   * 单一加/减/乘/除（不在本次重点）

2. 连续运算（无括号，按从左到右或结合律处理）

   * 连加（a + b + c + ...）
   * 连减（a - b - c - ...）
   * 连乘（a × b × c × ...）
   * 连除（a ÷ b ÷ c ÷ ...）
   * 加减混合（无括号，只有 + 和 -）
   * 加减乘除混合（无括号，不含括号时遵循乘除优先、同级左到右）

3. 含括号的混合运算

   * 单层括号（如 a + (b - c)）
   * 多层嵌套括号（如 (a+(b-c)) × (d - e)）

4. 包含特殊数字的乘除（影响速算策略）

   * 乘以 0 → 结果 0（短路）
   * 乘以 1 → 等于原数（可省操作）
   * 除以 1 → 等于原数
   * 除以 0 → 非法（错误）
   * 0 ÷ x → 0（当 x ≠ 0）

5. 混合带小数/整数/分数的运算（需数值类型规范化）

   * 包含小数时注意精度与格式化（context.precision）

这些题型可由解析器和分类器通过模式模板识别并分配到合适算子组。

---

# 2 解题技巧（心算/程序化策略汇总）

这些技巧用于算子实现和 Planner 的启发式优化（使步骤更自然、更易教学，也可减少运算量）：

* **优先级/括号规则**

  * 括号内先算，按从内到外展开（AST）。
  * 无括号时：乘除优先，乘除同级按左到右；加减同级按左到右。

* **结合律与交换律（用于合法重排）**

  * 加法/乘法：可使用结合律与交换律进行重组以便凑整或减少运算量。
  * 注意：减法与除法**不具备**通用交换律或结合律，只有在转换为加法/乘法（例如 a - b = a + (-b)，a ÷ b = a × (1/b)）并确认符号/倒数处理正确时，才可按规则变形（但必须记录步骤与验证）。

* **分配律（分解/凑整技巧）**

  * a × (b + c) = a×b + a×c（可用于简化含括号的乘法或把乘法分成易算的部分）。
  * 用于把乘法分配到和差上，尤其当 a 是特别数（如 10、100、0.5）时非常有效。

* **补数/凑整技巧（心算）**

  * 对于加减：把某一项调整为整十、整百后再补回（例如 53 - 28 → 53 - 30 + 2）。
  * 对于乘法：使用分解法（例如 6×47 = 6×(50-3) = 300 - 18）。
  * 对于除法：把除数变为接近的整数或因子，或把两边扩大（乘以 10^k）以便整除。

* **特殊数短路**

  * 任何乘法中出现 0 → 直接返回 0 并停止当前乘法子链（但仍需维护表达式层次的其余操作）。
  * 出现 1 → 可去除该乘因子（记录“省略 1”的步骤）。

* **交替策略（左到右或重排）**

  * 无括号时对加减混合问题，若所有都是 + 和 -，可安全地将其按结合律重组（因为 + 与 - 可转为 + 与 + 的形式加上符号），但当涉及乘除时，需保留乘除相对优先级。

* **舍入与精度控制**

  * 若包含小数并要求小数输出，使用 `Decimal` 按 context.precision 保证一致显示；内部运算仍用 `Fraction` 或高精度 `Decimal` 避免误差（取决于是否含分数）。

这些技巧在 Planner 中以启发式规则实现（match templates trigger particular rewrites）。

---

# 3 算子设计（题型 + 技巧的算子列表、匹配规则、解题分析步骤）

下面列出一组可注册的算子（operator）以覆盖所有题型。每个算子包含：

* **name**：算子名称
* **match_template**：解析器/分类器使用的匹配表达式模板（可转为 regex/AST pattern）
* **priority**：优先级（数值越小优先）；用于调度
* **steps**：逐步算法（可直接映射为 StepResult），包含操作码和简短公式/技巧注释

> 说明：算子按功能群组组织（解析器先调用识别算子获取候选，再由 Planner 生成执行序列）。模板使用 `{NUM}`, `{INT}`, `{DEC}`, `{EXPR}`, `{TERM}` 等占位符；`{TERM}` 指乘除项，`{EXPR}` 指任意子表达式（包括带括号）。

---

## 3.1 基础优先/括号算子

* **算子：括号优先（ParenthesesEvaluator）**

  * **match_template**：存在括号 `\(.+\)` 或 AST 节点类型 `Group`
  * **priority**：1
  * **steps**：

    1. 识别最内层括号（innermost）：`( ... )`。
    2. 将括号内表达式作为子问题交给 `ExpressionEvaluator`（递归）。
    3. 用子问题结果替换括号并记录步骤：`evaluate( ... ) -> value`。
    4. 继续直至无括号。
  * **技巧**：记录展开顺序，便于教学展示。

## 3.2 乘除优先算子

* **算子：乘除链求值（MulDivLeftToRight）**

  * **match_template**：连续 `{TERM} (*|/) {TERM} (*|/) ...` （无 + - 在该段）
  * **priority**：5
  * **steps**：

    1. 从左到右逐步执行乘或除：对每一步执行 `left op right`。
    2. 遇到 `*` 且任一为 0 → 记录短路步骤并把当前段结果设为 0（但仍需按表达式层级合并）。
    3. 遇到 `*` 且任一为 1 → 记录省略 1 的步骤（可优化为跳过）。
    4. 每步进行约分/化简（若有分数）。
  * **技巧**：在存在多个乘法项时可尝试因子重组以便出现 0/1 或便于心算（但必须可追溯）。

* **算子：乘法分配化简（DistributionOptimizer）**

  * **match_template**：`{TERM} * ({EXPR_with_plus_minus})` 或 `({EXPR_with_plus_minus}) * {TERM}`
  * **priority**：6（在 MulDivLeftToRight 之前可被选为优化）
  * **steps**：

    1. 判断 `TERM` 与括号内项的数值特征（是否易算，例如 10、100、0.5、整数且小）。
    2. 若适合，应用分配律：`a*(b+c)=a*b + a*c` 并生成相应子任务（记录分配公式）。
    3. 否则退回普通乘法处理。
  * **技巧**：优先分配当 `a` 为 10/100/1/0/-1 等，或当 `b+c` 中能凑整。

## 3.3 加减链算子

* **算子：加减链（AddSubLeftToRight）**

  * **match_template**：仅含 + 和 - 的表达式（无乘除）或子段（例如 `a + b - c + d`）
  * **priority**：8
  * **steps**：

    1. 将所有项转为带正负号的“加法”形式（把减法视为加上负数），例如 `a - b + c` → `a + (-b) + c`。
    2. 选择合适的重排策略（保持左到右或按结合律重组以便凑整）：

       * 若可通过重组使部分和为整十/整百/整数，则重组并记录“凑整”步骤（如 `53 + 28 + 19` → `(53 + 28) + 19` 或 `53 + (28+19)` 取最优）。
    3. 按选定顺序逐步相加并记录中间值。
  * **技巧**：优先把数与其补数配对（如 7 + 3 = 10），或把负数与正数配对消去。

## 3.4 混合无括号算子（MulDiv then AddSub）

* **算子：标准无括号混合求值（StandardOrderEvaluator）**

  * **match_template**：任意不含括号的表达式含 + - × ÷ 混合
  * **priority**：10
  * **steps**：

    1. 从左到右扫描，先识别并求值所有乘除连段（使用 `MulDivLeftToRight`），将它们作为中间项替换原式（记录每段中间结果）。
    2. 结果得到只有 + 和 - 的表达式，交给 `AddSubLeftToRight` 处理（如需，使用凑整策略）。
    3. 合并最终结果并执行格式化（整数/小数约定）。
  * **技巧**：对乘除段可在求值前尝试 `DistributionOptimizer`。

## 3.5 含括号混合运算算子（BracketedMixEvaluator）

* **算子：BracketedMixEvaluator**

  * **match_template**：表达式包含括号与混合运算
  * **priority**：2（高优先用于递归）
  * **steps**：

    1. 调用 `ParenthesesEvaluator` 处理最内层括号，得到替换后的表达式。
    2. 对无括号部分调用 `StandardOrderEvaluator`。
    3. 递归直至全式求解。
  * **技巧**：在处理括号内项时优先使用分配律以便减少计算（例如 a × (b ± c)）。

## 3.6 特殊数优化算子（SpecialNumbersOptimizer）

* **算子：0/1 优化（ZeroOneOptimizer）**

  * **match_template**：任一乘法/除法项等于 0 或 1，或加法含 0（如 `... + 0 + ...`）
  * **priority**：3（在乘除求值前应用）
  * **steps**：

    1. 扫描表达式子树：若乘段中有 0 → 将乘段结果设为 0，记录短路步骤。
    2. 若乘段中有 1 → 去除 1（记录省略步骤）。
    3. 若加法中有 0 → 去掉 0（记录省略步骤）。
  * **技巧**：在大规模表达式中能大幅减少计算节点。

## 3.7 重写/化简算子（RewriteOptimizer）

* **算子：凑整/补数重写（ComplementRewriting）**

  * **match_template**：出现容易凑整的模式（如 `x ± y` 中 x 末位为 0/5 等）
  * **priority**：7（在 AddSubLeftToRight 执行前可被调用）
  * **steps**：

    1. 识别可以通过 `±` 将某一项转换为整十/整百的场景（如 `53 - 28` → `53 - 30 + 2`）。
    2. 将表达式重写为等价形式并记录“凑整”转换步骤。
    3. 继续按标准求值。
  * **技巧**：尽可能减少中间进位/借位步骤以利于心算。

## 3.8 多项式/分配式算子（用于教学展示）

* **算子：分配法展开（ExpandByDistribution）**

  * **match_template**：乘法作用于和/差，或需要将大项分解（便于心算）
  * **priority**：9（可选）
  * **steps**：

    1. 展开 `a*(b+c)` 为 `a*b + a*c` 并把每项作为子任务。
    2. 记录展开公式并继续计算。
  * **技巧**：仅在能降低运算复杂度或便于整除时启用。

## 3.9 解析与格式化算子（Parser/Formatter）

* **算子：ExpressionParser**（注册为识别算子）

  * **match_template**：原始文本输入
  * **priority**：0（最先执行）
  * **steps**：解析 tokens -> AST，标注节点类型（Number, Operator, Group）并将数字规范化为 `Fraction`/`Decimal`。

* **算子：ResultFormatter**

  * **match_template**：任何 OperatorOutput 需要格式化时
  * **priority**：999（最终输出）
  * **steps**：根据 `context.display_style`（integer/fraction/decimal/precision）生成字符串/LaTeX 输出并记录格式化步骤。

---

### 样例：把解析器示例题映射到算子流程

* 题：`56+(53-28)`

  * Parser -> AST
  * BracketedMixEvaluator: 处理 `(53-28)` → AddSubLeftToRight → `25`（记录 `53 - 28 = 25`）
  * StandardOrderEvaluator: 56 + 25 = 81
  * Steps记录完整链路（括号先算 → 合并）

* 题：`1×4÷4`

  * MulDivLeftToRight: left-to-right

    * 1×4 = 4  （SpecialNumbersOptimizer may remove 1 earlier）
    * 4÷4 = 1
  * Result 1

* 题：`25÷(62-57)`

  * BracketedMixEvaluator: (62-57)=5
  * StandardOrderEvaluator: 25 ÷ 5 = 5

* 题：`94.7-(3.8-3.7)`

  * BracketedMixEvaluator: (3.8-3.7)=0.1
  * 94.7 - 0.1 = 94.6 (Decimal precision maintained by context)

---

# 4 算子规范化输出（StepResult 模板示例）

每一步应返回统一结构：

```json
{
  "description": "计算 53 - 28，使用凑整法：53 - 30 + 2",
  "operation": "rewrite_complement",
  "inputs": ["53", "28"],
  "result": "25",
  "formula": "53 - 28 = 53 - 30 + 2 = 25",
  "validation": true,
  "meta": {"technique":"凑整"}
}
```

最终 OperatorOutput（整体算子执行）保持与你提供过的 `算子输出格式` 一致（含 steps数组、step_count、formula、validation、success、error 字段）。

---

# 5 架构设计（Planner / Executor / Validator / Registry）

## 组件职责（工程导向）

* **Parser**：把输入转为 AST (`Expression`)；对数字进行类型归一（INT/DEC/Fraction）。（契约：`parse(text)->Expression`）
* **OperatorRegistry**：维护算子元数据（name, match_template, priority, supported_node_types）。算子以 Plugin 形式注册。
* **Classifier/Planner**：基于 AST，按节点类型与模板从 Registry 检索匹配算子候选，计算 `match_score`，选出主算子或算子序列（Planner 生成执行计划）。 Planner 负责决策：是否启用优化算子（如 DistributionOptimizer、ComplementRewriting）。
* **Executor**：按计划执行算子序列，接收每步 StepResult，合并中间结果到 AST（或替换节点），记录时间/验证信息。
* **Validator**：对每步结果进行本地验证（例如：交叉乘法、重算或使用高精度 baseline），并标注 `validation`。
* **Formatter**：把最终结果与步骤转换为展示格式（text/LaTeX/JSON）。
* **Audit Logger**：记录整个流程（输入、选择的算子、每步耗时、错误、最终结果），支持回溯与教学分析。

## 算子接口契约（简洁）

```python
class Operator:
    name: str
    priority: int
    match_template: str

    def is_match(self, node: ASTNode) -> MatchResult:
        # MatchResult: {matched: bool, score: float, reason: str}
        pass

    def plan(self, node: ASTNode, context: Context) -> Plan:
        # 返回一组子算子或步骤计划
        pass

    def execute(self, node: ASTNode, context: Context) -> StepResult:
        # 运行此算子，返回 StepResult 并可能替换 AST 节点
        pass
```

## Planner 伪逻辑（高层）

1. 若 AST 有 Group 节点（括号），选择 `ParenthesesEvaluator` 优先调度。
2. 对当前 AST 段，获取候选算子（registry.filter_by_node_type），按 `score` 和 `priority` 排序。
3. 选择 top-k 候选，评估 `cost_estimate` 与 `benefit`（启发式，benefit=是否能减少操作/产生整数/触发短路），决定是否使用优化算子。
4. 生成执行计划（可能递归），交给 Executor。

---

# 6 错误处理与边界条件

* **除以 0**：在任何除法执行前先执行 `zero_check`，若发现除数为 0，返回 `error.code=DIV_BY_ZERO` 并在 steps 中说明。
* **非法语法**：Parser 抛 `PARSE_ERROR`，并给出位置信息与 `hint`（例如预期的运算符或括号不匹配）。
* **浮点精度问题**：在表达式含小数时，内部运算使用 `Decimal`/`Fraction` 策略由 context 指定。若转换会丢失精度，标注 `approximate:true`。
* **超大整数**：使用 Python 大整数；若超出预设上限（罕见），返回 `error.code=OVERFLOW` 并给出建议（使用 BigInt 模式）。

---

# 7 测试用例（参考并覆盖你给的题目）

将你给的样例题作为回归测试集。每题应包含：

* 原始输入字符串
* 期望 AST（或至少规范化 operands）
* 期望步骤链（至少关键步骤）
* 期望最终结果与 display_style（string）

示例（部分）：

* `56+(53-28)` → steps: `(53-28)=25` → `56+25=81` → result `81`
* `66-2+2` → as add/sub chain; planner may rearrange to `66 - 2 + 2 = 66 + (-2) + 2 = 66` → result `66`
* `1×4÷4` → muldiv LTR: `1×4=4` → `4÷4=1` → result `1`
* `25÷(62-57)` → bracketed: `(62-57)=5` → `25÷5=5`

编写单元测试确保每题的步骤链中包含关键转换（例如括号先算、凑整重写、0/1短路等）。

---

# 8 性能、可扩展性、和工程实施要点

* **懒加载算子**：Registry 支持按需加载算子插件，减少系统启动成本。
* **可配置优化级别**：Context 中带 `optimization_level`（0=无优化, 1=只安全优化, 2=启用心算重写）以平衡可解释性与速度。教学场景建议低优化以保留教学步骤，自动批改场景可开高优化。
* **审计与可追溯**：每一步须保留输入/输出与算子元信息，便于回放教学与错误分析。
* **并行/批处理**：对于大批量题目支持批处理并行化；算子为纯函数，应易于并行执行。
* **格式化策略**：输出结果需统一 `display_style`（fraction/integer/decimal/mixed），并由 Formatter 处理，而非算子决定（除非题目 context 指定）。

---

# 9 文档交付清单（建议）

1. 算子元数据 JSON（包含所有上文算子 name/priority/match_template/steps），便于注册器加载。
2. Planner & Executor 接口文档（API契约）。
3. Parser 文档（支持语法、token、支持输入样例）。
4. 回归测试集（包含你提供的样例与扩展角落案例，如 0/1、负数、小数、长链）。
5. 示例运行（示例输入 -> 步骤 JSON -> 最终输出）若需要我可以生成若干题目的示例运行输出。

---