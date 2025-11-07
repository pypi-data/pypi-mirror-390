下面给出**符合你项目工程技术标准**、面向“分数算子系统（Fraction Operators）”的**完整设计方案**与**算子清单输出**。方案聚焦标准化、架构、算法描述、接口契约与可验证执行流程，去除多余实现细节，但保留所有分数题型算子的名称、适用条件、分步骤解题规则、速算技巧与验证规范，便于直接纳入你现有的 Units 风格工程（算子注册器、引擎、优先级调度、格式化输出等）。

---

# 一、方案总体定位（工程规范视角）

目标：设计一个**高可靠、可扩展、可审计**的分数计算与解析算子系统，使小学分数题可被结构化识别、规则化拆解为算子序列并可程序化求解与校验。必须满足工程标准：模块化、接口契约、可注册算子、算子优先级、可验证步骤输出、精确数值（使用 Python `fractions.Fraction` 与 `decimal.Decimal` 做转换/展示），强鲁棒输入解析（LaTeX、常见文本、带分数、百分数、小数混合）、严格错误处理与审计日志。

设计原则：

* **最小权限算子**：每个算子完成单一、可验证的变换或判断（便于组合与测试）。
* **纯函数/无副作用**：算子返回 `StepResult` 而非直接修改全局状态；执行引擎负责状态聚合。
* **可验证步骤链**：每一步包含 `operation, inputs, outputs, formula, validation` 字段，方便教学和审计。
* **优先级/匹配度调度**：引擎基于 `is_match`（模式匹配）与 `priority` 选择算子。
* **标准输出契约**：统一 JSON 输出结构（同你给的算子输出格式），包含步骤数组、最终结果、验证标志与错误信息。

---

# 二、架构与核心模块（文件与职责）

与 `Units` 工程风格一致，建议目录结构（仅描述职责，减少实现细节）：

* `fraction_types.py`

  * 定义数据模型（`FracOperand`, `Problem`, `StepResult`, `OperatorSpec`），枚举与常量（表示 answer_form、display_style）。
  * 指定序列化/反序列化契约（支持 LaTeX `\frac{}`, 带分数 `a b/c`、小数、百分数）。

* `parser.py`

  * 解析器：把原始文本/LaTeX/结构化输入转为 `Problem`，识别 `kind`（fraction/decimal/mixed/percent/integer）与 `Fraction` 规范表示。必须支持错位容错（空格、多种分割符）。

* `operator_base.py`

  * 算子基类 `FractionOperator`：定义接口（`is_match(problem) -> MatchScore`、`solve(problem) -> StepResult`、`metadata`），并包含优先级、稳定性标签、可逆性标注。

* `operator_registry.py`

  * 算子注册器：采用工厂 + 注册表模式，启动时加载所有算子元数据（支持动态插件目录），并按 `priority` 与 `match_score` 排序。

* `engine.py`

  * 执行引擎：负责题型识别（调用若干算子获得匹配度）、算子序列选择、步骤串联执行、结果合并与最终验证（可选择多种答案格式输出）。

* `operators/`

  * 每个文件按题型组织算子实现（如 `add_same_den.py`, `div_frac_frac.py`, `reciprocal.py`, `reduce.py` 等）。每个算子仅实现其 `is_match` 与 `solve`（返回步骤详细信息符合契约）。

* `validator.py`

  * 结果验证工具：检查每一步计算一致性；例如交叉相乘比较、约分后等价检验、最终结果与高精度参考计算的一致性（默认使用 Fraction 作为参考）。

* `formatter.py`

  * 输出器：把 `StepResult` 转换为工程指定的 JSON 算子输出格式（你给的格式），并支持 LaTeX/文本/混合输出。

* `tests/`

  * 单元与合约测试：算子级测试、引擎端到端测试、边界情况（0、负数、无限循环小数、除以0）测试。

---

# 三、核心算法/规则规范（抽象描述，便于工程实现）

## 1. 数据规范（契约）

* `FracOperand`：包含 `raw`, `kind`, `fraction: Fraction`, `is_mixed: bool`, `original_format`（LaTeX/text）等字段。
* `Problem`：包含 `id`, `operator_token`（+ - * / compare reciprocal convert 等），`operands: List[FracOperand]`, `context`（answer_form、precision、display_style）。
* `StepResult`（每步）契约：

  * `description` (string)
  * `operation` (string, 操作码)
  * `inputs` (list of operand refs)
  * `result` (string or Fraction)
  * `formula` (string|null)
  * `validation` (bool)
  * `meta` (optional explanations, speedtips)
* `OperatorOutput`（最终）契约同你给的样例 JSON：包含 `steps`, `step_count`, `formula`, `validation`, `success`, `error`。

## 2. 数值处理原则

* **内部计算基准**：全部使用 `fractions.Fraction` 进行精确算术，只有在 `context.answer_form == 'decimal'` 或显示时，才使用 `Decimal`（并按 `precision` 显式转换）。
* **约分规范**：规范化结果必须保证分母 > 0。约分采用 `gcd`。带分数展现与否由 `context.display_style` 决定。
* **小数/百分数互转**：转换前判断是否为有限小数（分母的质因数仅为 2 与 5），否则标注“循环小数”并按 `precision` 截断或返回循环节。
* **错误处理**：遇到除以 0、非法格式、不可解析输入，返回 `success:false`, `error` 含可读消息，并在 `steps` 中给出诊断建议。

## 3. 算子匹配与优先级

* `is_match(problem)` 返回结构 `{"match": bool, "score": float, "reason": str}`。匹配引擎按 `score`（结合 operator `priority`）选择最合适算子序列。
* `priority`：整数，值越小优先级越高（或反向，统一文档定义并执行）。建议：基础算子（如约分、解析）优先级高（低数值），复杂题型组合算子优先级略低。

## 4. 步骤化求解管线（通用模式）

1. **解析阶段**（Parser）→ `Problem`
2. **规范化阶段**（Normalize）→ 约分/带分转假分/小数转分数（根据需要）
3. **识别阶段**（Classifier）→ 得到题型候选列表
4. **计划阶段**（Planner）→ 根据题型选出算子序列（例如 `div_frac_frac` → [reciprocal, cross_reduce, multiply, normalize]）
5. **执行阶段**（Executor）→ 逐算子执行并记录 `StepResult`
6. **验证阶段**（Validator）→ 每步与最终结果用 `Fraction` 做一致性验证
7. **格式化输出**（Formatter）→ JSON 返回

---

# 四、算子清单（完整保留并标准化）

下面**以你要求的 JSON 算子输出格式**，把所有小学分数题型算子逐一列出（每个算子都遵循输出字样）。**为了便于工程直接使用，我把每个算子都给出：名称、说明、优先级、分步骤执行说明、公式、验证标志、成功/错误结构**。每个算子的 `result` 字段在通用模板中为 `null`（执行时由引擎填充）；此处给出示例 `result` 仅在非常简单可静态推断的情况下填值（一般保持 `null`）。注意：每个算子的 `steps` 描述为算法层面的步骤（便于实现与教学展现）。

> 说明：算子数量与你的题型表一一对应，尽可能完整覆盖你提供的题型（包含分数与小数/百分数互化、比较、约分、带分数/假分数、各种乘除法情形等）。下列 JSON 数组可直接加载到 `operator_registry`，引擎按 `is_match` 调用。

```json
[
  {
    "name": "约分（简化分数）",
    "description": "将分数化为最简形式；若需要，可转为带分数",
    "priority": 10,
    "result": null,
    "steps": [
      {
        "description": "标准化分子分母并确保分母为正",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      },
      {
        "description": "计算 gcd(numer, denom)，两者同时除以 gcd",
        "operation": "gcd_reduce",
        "result": null,
        "formula": "numer' = numer/gcd, denom' = denom/gcd"
      },
      {
        "description": "若要求带分数且 abs(numer') >= denom'，转换为带分数",
        "operation": "to_mixed_if_needed",
        "result": null,
        "formula": "mixed = floor(numer'/denom') + (numer'%denom')/denom'"
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "Fraction(numer,denom) -> reduced",
    "success": true,
    "error": null
  },
  {
    "name": "倒数（求逆）",
    "description": "求分数的倒数（reciprocal）；带分数先转为假分数",
    "priority": 8,
    "result": null,
    "steps": [
      {
        "description": "检查分数是否为0（若为0，返回错误：无倒数）",
        "operation": "zero_check",
        "result": null,
        "formula": null
      },
      {
        "description": "若为带分数，先转为假分数；然后交换分子与分母",
        "operation": "reciprocal",
        "result": null,
        "formula": "reciprocal(a/b) = b/a"
      },
      {
        "description": "约分标准化倒数结果",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "1/(a/b) = b/a",
    "success": true,
    "error": null
  },
  {
    "name": "分数与小数互化",
    "description": "分数与小数相互转换，检测是否为有限小数或循环小数；按精度/循环节输出",
    "priority": 12,
    "result": null,
    "steps": [
      {
        "description": "约分分数；检查分母的质因数是否仅包含2和5",
        "operation": "prime_factor_check",
        "result": null,
        "formula": null
      },
      {
        "description": "若仅含2和5，计算有限小数（exact division）；否则标注循环小数并返回循环节或按精度截断",
        "operation": "to_decimal_or_repeating",
        "result": null,
        "formula": "decimal = numer/denom"
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "a/b -> decimal or repeating",
    "success": true,
    "error": null
  },
  {
    "name": "分数与百分数互化",
    "description": "把分数转换为百分数，或把百分数转为分数（并约分）",
    "priority": 12,
    "result": null,
    "steps": [
      {
        "description": "若由分数到百分数：乘以100并附上%符号；再约分",
        "operation": "fraction_to_percent",
        "result": null,
        "formula": "percent = (numer/denom) * 100%"
      },
      {
        "description": "若由百分数到分数：去掉%并除以100，转为分数后约分",
        "operation": "percent_to_fraction",
        "result": null,
        "formula": "fraction = percent/100"
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "a/b <-> (a/b)*100%",
    "success": true,
    "error": null
  },
  {
    "name": "同分母分数加法（同分母相加）",
    "description": "分母相同的分数直接相加分子，最后约分/转带分数",
    "priority": 6,
    "result": null,
    "steps": [
      {
        "description": "确认所有分数分母相同（若不相同则退回异分母处理）",
        "operation": "确认所有分数分母相同",
        "result": null,
        "formula": null
      },
      {
        "description": "分子相加，分母保持不变",
        "operation": "分子相加",
        "result": null,
        "formula": "结果 = (分子 + 分子) / 分母"
      },
      {
        "description": "约分并按需要转为带分数",
        "operation": "约分",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "a/d + b/d = (a+b)/d",
    "success": true,
    "error": null
  },
  {
    "name": "同分母分数减法",
    "description": "分母相同的分数直接相减分子，最后约分/带分数转换",
    "priority": 6,
    "result": null,
    "steps": [
      {
        "description": "检查同分母条件",
        "operation": "检查是否同分母",
        "result": null,
        "formula": null
      },
      {
        "description": "分子相减，保留符号",
        "operation": "subtract_numerators",
        "result": null,
        "formula": "result = (a-b)/d"
      },
      {
        "description": "约分、格式化输出",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "a/d - b/d = (a-b)/d",
    "success": true,
    "error": null
  },
  {
    "name": "异分母分数加法（通分法）",
    "description": "对不同分母的分数求最小公倍数（lcm），调整分子后相加",
    "priority": 7,
    "result": null,
    "steps": [
      {
        "description": "计算分母的最小公倍数（lcm）",
        "operation": "计算分母的最小公倍数",
        "result": null,
        "formula": "lcm = lcm(d1, d2, ...)"
      },
      {
        "description": "将每个分数按 lcm 扩分子： numer * (lcm/denom)",
        "operation": "adjust_numerators_to_lcm",
        "result": null,
        "formula": "adj_numer = numer * (lcm/denom)"
      },
      {
        "description": "相加调整后的分子，分母为 lcm，最后约分",
        "operation": "add_numerators_then_reduce",
        "result": null,
        "formula": "result = sum(adj_numer)/lcm"
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "a/b + c/d = (a*(lcm/b) + c*(lcm/d))/lcm",
    "success": true,
    "error": null
  },
  {
    "name": "异分母分数减法",
    "description": "与异分母加法同理，调整分子后相减",
    "priority": 7,
    "result": null,
    "steps": [
      {
        "description": "计算 lcm，并扩分子",
        "operation": "计算分母的最小公倍数_and_adjust",
        "result": null,
        "formula": null
      },
      {
        "description": "调整后分子相减",
        "operation": "subtract_adjusted_numerators",
        "result": null,
        "formula": "result = adj_a - adj_b / lcm"
      },
      {
        "description": "约分与带分数转换（如需）",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "a/b - c/d = (a*(lcm/b) - c*(lcm/d))/lcm",
    "success": true,
    "error": null
  },
  {
    "name": "分数乘分数（乘法）",
    "description": "两个分数相乘，优先交叉约分以减少运算规模，再相乘分子与分母",
    "priority": 5,
    "result": null,
    "steps": [
      {
        "description": "将带分数转为假分数（如有）",
        "operation": "to_improper_if_needed",
        "result": null,
        "formula": null
      },
      {
        "description": "尝试交叉约分：约分左分子与右分母，左分母与右分子",
        "operation": "cross_reduce",
        "result": null,
        "formula": null
      },
      {
        "description": "分子相乘，分母相乘；约分并标准化",
        "operation": "multiply_and_reduce",
        "result": null,
        "formula": "(a/b)*(c/d) = (a*c)/(b*d)"
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "(a/b)*(c/d) = (a*c)/(b*d)",
    "success": true,
    "error": null
  },
  {
    "name": "分数乘整数",
    "description": "分数与整数相乘，可以先约分整数与分母再乘",
    "priority": 5,
    "result": null,
    "steps": [
      {
        "description": "若整数与分母有公因子，先约掉以简化计算",
        "operation": "reduce_integer_with_denom",
        "result": null,
        "formula": null
      },
      {
        "description": "分子乘以整数，分母保持；约分与转格式",
        "operation": "multiply_numer_by_int",
        "result": null,
        "formula": "(a/b)*n = (a*n)/b"
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "(a/b)*n",
    "success": true,
    "error": null
  },
  {
    "name": "分数乘小数",
    "description": "将小数转为分数（移位）或将分数转为小数，按约定输出格式执行",
    "priority": 9,
    "result": null,
    "steps": [
      {
        "description": "将小数转为等价分数（去小数点，分母为10^k）或将分数转为小数（若更便捷）",
        "operation": "decimal_to_fraction_or_choice",
        "result": null,
        "formula": null
      },
      {
        "description": "按分数乘法规则操作（交叉约分→乘→约分）",
        "operation": "multiply_frac_frac",
        "result": null,
        "formula": null
      },
      {
        "description": "若 answer_form 要求小数，执行分数到小数的转换并按精度格式化",
        "operation": "fraction_to_decimal_if_requested",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "（适用）",
    "success": true,
    "error": null
  },
  {
    "name": "带分数↔假分数互转",
    "description": "带分数与假分数互相转换，作为基础算子被其它算子复用",
    "priority": 4,
    "result": null,
    "steps": [
      {
        "description": "带分数 a b/c -> 假分数 (a*c + b)/c；假分数 p/q -> 整数 + 余数/q",
        "operation": "to_improper_or_to_mixed",
        "result": null,
        "formula": "improper = whole*denom + numer"
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "mixed <-> improper",
    "success": true,
    "error": null
  },
  {
    "name": "分数除以分数",
    "description": "除以分数等价乘以倒数，先求倒数再乘，交叉约分以简化",
    "priority": 5,
    "result": null,
    "steps": [
      {
        "description": "检查被除数非0；将除数取倒数",
        "operation": "reciprocal_and_check",
        "result": null,
        "formula": "a/b ÷ c/d -> a/b × d/c"
      },
      {
        "description": "交叉约分然后按乘法规则计算",
        "operation": "cross_reduce_and_multiply",
        "result": null,
        "formula": null
      },
      {
        "description": "约分并格式化（带分数/假分数/小数）",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "a/b ÷ c/d = (a*d)/(b*c)",
    "success": true,
    "error": null
  },
  {
    "name": "分数除以整数",
    "description": "分数 ÷ 整数 = 分数 / (整数)，可把整数视为分母相乘",
    "priority": 6,
    "result": null,
    "steps": [
      {
        "description": "将除法写作分数相乘： (a/b) ÷ n = a/(b*n)",
        "operation": "turn_div_frac_int_into_frac",
        "result": null,
        "formula": "(a/b) ÷ n = a/(b*n)"
      },
      {
        "description": "约分并输出",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "(a/b) ÷ n",
    "success": true,
    "error": null
  },
  {
    "name": "分数除以小数",
    "description": "将小数转为分数（或把两边同时放大），然后按分数除法处理",
    "priority": 9,
    "result": null,
    "steps": [
      {
        "description": "把小数转为分数（x/10^k），把被除数相应放大或直接转为分数",
        "operation": "decimal_to_fraction",
        "result": null,
        "formula": null
      },
      {
        "description": "调用分数除法算子（倒数乘法）",
        "operation": "div_frac_frac",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "a/b ÷ decimal",
    "success": true,
    "error": null
  },
  {
    "name": "分数比较大小（一般）",
    "description": "比较两个分数的大小，优先使用交叉乘法以避免通分开销",
    "priority": 3,
    "result": null,
    "steps": [
      {
        "description": "若同分母：直接比较分子大小；若同分子：分母小者更大",
        "operation": "fast_path_same_denom_or_same_numer",
        "result": null,
        "formula": null
      },
      {
        "description": "否则使用交叉相乘比较： compare numer1*denom2 ? numer2*denom1",
        "operation": "cross_multiply_compare",
        "result": null,
        "formula": "a/b ? c/d  <=> a*d ? c*b"
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "compare by cross multiplication",
    "success": true,
    "error": null
  },
  {
    "name": "分数的意义与基本判断",
    "description": "判断分数大小与单位意义（如 1/2 > 1/5 等基础判断规则）",
    "priority": 2,
    "result": null,
    "steps": [
      {
        "description": "对比分母或分子简易规则（为教学提示而非复杂计算）",
        "operation": "heuristic_compare",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "simple fraction comparisons",
    "success": true,
    "error": null
  },
  {
    "name": "分数的初步认识与简单加减",
    "description": "基础题型识别与直接计算（常用于低年级题库化）",
    "priority": 2,
    "result": null,
    "steps": [
      {
        "description": "直接应用同分母/异分母加减算子并输出简洁步骤",
        "operation": "delegate_to_add_sub_operators",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "基础算数规则",
    "success": true,
    "error": null
  },
  {
    "name": "分数化百分数",
    "description": "将分数转换为百分数（乘100），并按需输出整数百分数或保留小数位",
    "priority": 11,
    "result": null,
    "steps": [
      {
        "description": "计算 (numer/denom)*100，并按 context.precision 格式化",
        "operation": "fraction_to_percent",
        "result": null,
        "formula": "(a/b)*100%"
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "fraction -> percent",
    "success": true,
    "error": null
  },
  {
    "name": "分数乘法一般算子（通用）",
    "description": "通用乘法管线，支持分数/整数/小数通用输入（内部转成分数后计算）",
    "priority": 5,
    "result": null,
    "steps": [
      {
        "description": "规范化所有操作数为 Fraction 表示",
        "operation": "normalize_all_operands",
        "result": null,
        "formula": null
      },
      {
        "description": "依次执行交叉约分和乘法，逐步记录中间值",
        "operation": "iterative_cross_reduce_multiply",
        "result": null,
        "formula": null
      },
      {
        "description": "最终约分并按需要转换为带分数或小数",
        "operation": "final_normalize_and_format",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "general multiply flow",
    "success": true,
    "error": null
  },
  {
    "name": "分数除法一般算子（通用）",
    "description": "通用除法管线，支持分数/整数/小数通用输入（转分数后取倒数再乘）",
    "priority": 5,
    "result": null,
    "steps": [
      {
        "description": "规范化并检查除数是否为0",
        "operation": "normalize_and_check_zero",
        "result": null,
        "formula": null
      },
      {
        "description": "取除数倒数并调用乘法管线",
        "operation": "reciprocal_then_multiply",
        "result": null,
        "formula": null
      },
      {
        "description": "约分并格式化输出",
        "operation": "normalize_fraction",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 3,
    "validation": true,
    "formula": "general division flow",
    "success": true,
    "error": null
  },
  {
    "name": "同分母分数大小比较",
    "description": "快速比较同分母分数大小（直接比较分子）",
    "priority": 2,
    "result": null,
    "steps": [
      {
        "description": "确认分母相同，直接比较分子大小",
        "operation": "compare_numerators",
        "result": null,
        "formula": "if d1==d2 then a1? a2"
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "same denom compare",
    "success": true,
    "error": null
  },
  {
    "name": "异分母分数大小比较",
    "description": "通过交叉相乘或通分比较异分母分数大小",
    "priority": 3,
    "result": null,
    "steps": [
      {
        "description": "使用交叉相乘避免完整通分：比较 a1*d2 ? a2*d1",
        "operation": "cross_multiply_compare",
        "result": null,
        "formula": "a/b ? c/d  <=> a*d ? c*b"
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "cross multiplication",
    "success": true,
    "error": null
  },
  {
    "name": "百分数特殊转换（百分数→分数→小数）",
    "description": "处理百分数题型，例如 '7/2 = ?%' 或 '%→分数' 等",
    "priority": 11,
    "result": null,
    "steps": [
      {
        "description": "识别百分数表达；若题目为 fraction -> percent，执行乘100；反向则除以100并约分",
        "operation": "percent_fraction_pipeline",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "percent <-> fraction",
    "success": true,
    "error": null
  },
  {
    "name": "分数题型识别算子（Classifier）",
    "description": "负责把原始 Problem 映射到具体算子/题型（返回候选列表并带匹配度）",
    "priority": 1,
    "result": null,
    "steps": [
      {
        "description": "解析操作符与操作数类型，基于模式库（同分母/异分母/乘/除/compare/convert/reciprocal等）生成候选算子并打分",
        "operation": "pattern_match_and_score",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 1,
    "validation": true,
    "formula": "classification by pattern rules",
    "success": true,
    "error": null
  },
  {
    "name": "复杂表达式求值（含括号与多运算）",
    "description": "把复杂表达式拆成二元子问题（遵循运算优先级），逐步调用基础算子求解并记录步骤",
    "priority": 15,
    "result": null,
    "steps": [
      {
        "description": "解析表达式树（AST），按运算优先级自底向上分解为算子任务",
        "operation": "expression_to_tasks",
        "result": null,
        "formula": null
      },
      {
        "description": "对每个子任务选择合适算子执行并合并中间结果",
        "operation": "task_scheduler_and_executor",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "AST-evaluation with fraction ops",
    "success": true,
    "error": null
  },
  {
    "name": "带分数题型（教学展示）",
    "description": "把结果以带分数形式展示（如果题目或上下文要求），并生成带分数转换步骤",
    "priority": 4,
    "result": null,
    "steps": [
      {
        "description": "将假分数转换为带分数并明确整数部分与余数",
        "operation": "to_mixed",
        "result": null,
        "formula": "int = numer // denom, rem = numer % denom"
      },
      {
        "description": "格式化带分数输出（含教学提示）",
        "operation": "format_mixed_output",
        "result": null,
        "formula": null
      }
    ],
    "step_count": 2,
    "validation": true,
    "formula": "improper -> mixed",
    "success": true,
    "error": null
  }
]
```

---

# 五、算子系统设计细节规范（标准化说明，便于 QA 与评审）

## 算子接口契约（高层）

* `is_match(problem: Problem) -> MatchResult`

  * `MatchResult` = `{ matched: bool, score: float, reason: str }`
  * `score` 取值范围 0..1 或 0..100，便于引擎排序
* `solve(problem: Problem, config: SolveConfig) -> OperatorOutput`

  * 返回结构需符合前述 JSON `OperatorOutput` 契约（含步骤细节）。
* 每个算子需声明 `metadata`: `{ name, description, priority, supported_kinds, stability, cost_estimate }`

## 引擎行为准则

* **优先选择低 cost、score 高的算子**；若多个算子 score 接近且 priority 相同，引擎用 deterministic tie-break（例如按名称排序）以保证可复现性。
* **每步都必须可验证**：算子应在 `StepResult.validation` 中提供本步的真实性检查（例如交叉乘法比较、约分后等价性检验）。
* **错误语义统一**：返回 `error` object 包含 `code`, `message`, `hint`（指示如何修正输入或设置）。
* **审计日志**：引擎将每次算子匹配结果、执行耗时、内存及中间结果记录到审计日志（便于线上问题追踪与教学分析）。

## 性能与可扩展性约定

* 基本算子均为轻量整数运算（`Fraction` 用整数），能处理大数（Python 大整数支持）；若遇到超大数或需要浮点近似，算子须标注 `approximate:true` 并在步骤中注明。
* 算子注册采用惰性加载（按需实例化）以减少启动开销；支持热插拔（可在运行时注册/注销实验算子）。

---

# 六、验证与质量保证（测试规范）

每个算子必须拥有：

* **单位测试**：覆盖正常路径、边界值（除以0、分母负值、带分数、格式不规范）。
* **合约测试**：输入 Problem -> 输出 OperatorOutput 符合 JSON 格式，并且 `validation` 为 true。
* **回归题集**：使用你提供的题库（knowledge table）作为回归集，确保每个题型被正确识别并给出正确步骤与结果。
* **行为测试**：检验引擎在多个算子可用时选择正确算子并给出可复现步骤链。

---

# 七、可交付项（建议里程碑）

1. 设计文档（本方案）— ✅（当前）
2. 算子元数据 JSON（上文算子清单）— ✅（当前）
3. Parser + 基础算子（约分、通分、乘、除、比较、倒数）实现与单元测试 — 可交付
4. 引擎与注册器框架实现（契约接口、调度） — 可交付
5. 测试集（使用你给的知识表作为样例）与结果对照 — 可交付
6. 文档化（API 文档、算子说明、错误码规范） — 可交付

---

# 八、如何在你现有 Units 工程中接入

* 把 `fraction_types.py`, `parser.py`, `operator_base.py`, `operator_registry.py`, `engine.py` 放入 `calculators/` 的子目录 `fraction_calculators/`。
* 在 `register.py` 中添加 fraction 部署点，按你已有 Units 注册机制注册算子元数据（name、priority、supported_kinds）。
* 使用同样的 `Result` 输出契约（你示例中的 `Result` 结构），以便上层系统统一消费与呈现。

---
