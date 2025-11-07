"""
小学数学单位换算自动解析引擎
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from .base_types import UnitType, UnitProblem, UnitValue, UnitCalculator, ConversionStep
from .calculators.length import LengthUnitCalculator
from .calculators.time import TimeUnitCalculator
from .calculators.mass import MassUnitCalculator
from .calculators.currency import CurrencyUnitCalculator
from .calculators.number import NumberUnitCalculator
from .register import UnitCalculatorRegister
from ..base.engine import BaseEngine, ConversionStep

unit_names = ['元', '角', '分', 'km', 'm', 'cm', 'mm', 'kg', 'g', 't', '千克','吨', '克', '年', '月', '日', '时', '分', '秒', '亿', '万', '千', '百']
unit_names += ['千米', '公里', '分米', '毫米', '公斤', '平方米', '平方米', '平方千米', '平方公里', '平方分米', '平方厘米', '平方毫米', '公顷']
unit_names += ['立方米', '立方分米', '立方厘米', '升', '毫升', 'm³', 'm^3', 'dm³', 'dm^3', 'cm³', 'cm^3', 'L', 'mL']
cn_chars = '零一二三四五六七八九十'

class UnitConversionEngine(UnitCalculatorRegister, BaseEngine):
    """单位换算解析引擎"""
    
    def __init__(self):
        self.calculators: List[UnitCalculator] = []
        self.unit_type_mapping = self._initialize_unit_mapping()
        self._register_calculators()

    def is_match_pattern(self, expression: str) -> bool:
        """判断是否为匹配的单位换算问题"""
        try:
            problem = self.parse_problem(expression)
            if problem is None or problem.unit_type == UnitType.UNKNOWN:
                return False
            return any(calculator.is_match_pattern(problem) for calculator in self.calculators)
        except:
            return False
    
    def _initialize_unit_mapping(self) -> Dict[str, UnitType]:
        """初始化单位类型映射"""
        return {
            # 长度单位
            "km": UnitType.LENGTH, "千米": UnitType.LENGTH, "公里": UnitType.LENGTH,
            "m": UnitType.LENGTH, "米": UnitType.LENGTH,
            "dm": UnitType.LENGTH, "分米": UnitType.LENGTH,
            "cm": UnitType.LENGTH, "厘米": UnitType.LENGTH,
            "mm": UnitType.LENGTH, "毫米": UnitType.LENGTH,
            
            # 时间单位
            "年": UnitType.TIME, "year": UnitType.TIME,
            "月": UnitType.TIME, "month": UnitType.TIME,
            "h": UnitType.TIME, "时": UnitType.TIME, "小时": UnitType.TIME,
            "min": UnitType.TIME, "分": UnitType.TIME, "分钟": UnitType.TIME,
            "s": UnitType.TIME, "秒": UnitType.TIME, "分": UnitType.TIME, 
            "日": UnitType.TIME, "天": UnitType.TIME, "day": UnitType.TIME,
            
            # 质量单位
            "t": UnitType.MASS, "吨": UnitType.MASS,
            "kg": UnitType.MASS, "千克": UnitType.MASS, "公斤": UnitType.MASS,
            "g": UnitType.MASS, "克": UnitType.MASS,
            
            # 货币单位
            "元": UnitType.CURRENCY, "¥": UnitType.CURRENCY,
            "角": UnitType.CURRENCY, "jiao": UnitType.CURRENCY,
            "fen": UnitType.CURRENCY,
            
            # 数字单位
            "亿": UnitType.NUMBER, "千万": UnitType.NUMBER, "百万": UnitType.NUMBER,
            "十万": UnitType.NUMBER, "万": UnitType.NUMBER, "千": UnitType.NUMBER, "百": UnitType.NUMBER,

            # 计量单位
            "折": UnitType.DISCOUNT, '%': UnitType.PERCENTAGE,  '个': UnitType.PERCENTAGE

            # 面积单位
            , "m²": UnitType.AREA, "平方米": UnitType.AREA, "dm²": UnitType.AREA, "平方分米": UnitType.AREA
            , "cm²": UnitType.AREA, "平方厘米": UnitType.AREA, "mm²": UnitType.AREA, "平方毫米": UnitType.AREA
            , "平方千米": UnitType.AREA, "平方公里": UnitType.AREA, '公顷': UnitType.AREA, '亩': UnitType.AREA

            # 体积单位
            , "m³": UnitType.VOLUME, "m^3": UnitType.VOLUME, "立方米": UnitType.VOLUME, "dm³": UnitType.VOLUME
            , "dm^3": UnitType.VOLUME, "立方分米": UnitType.VOLUME, "cm³": UnitType.VOLUME, "cm^3": UnitType.VOLUME,
            "立方厘米": UnitType.VOLUME, "L": UnitType.VOLUME, "升": UnitType.VOLUME, "mL": UnitType.VOLUME, "毫升": UnitType.VOLUME
            , "毫升": UnitType.VOLUME
        }
    
    def _register_calculators(self):
        """注册所有单位换算算子"""
        self._register_default_calculators()
    def parse_zhe(self, text: str, unit_name='折') -> str:
        """解析折扣表达式"""
        text = text.replace('@%', '=@%').replace('==', '=').replace(' ', '')
        # 替换中文数字为阿拉伯数字
        numbers = []
        idx_left = text.find('=')
        for idx, char in enumerate(text[:idx_left]):
            idx = cn_chars.find(char)
            if idx != -1:
                numbers.append(idx)
        remaining_text = text[idx_left:]
        if len(numbers) > 0:
            result = '.'.join([str(n) for n in numbers]) + unit_name
            text = result + remaining_text
            print(f"解析折扣表达式，转换结果：{text}")
            self.pre_steps = [
                ConversionStep(description="将中文数字转换为阿拉伯数字",
                                operation="中文数字转换", result=result)]
        return text
    
    def parse_problem(self, text: str) -> UnitProblem:
        """解析单位换算题目文本"""
        # 去除多余空格
        self.pre_steps = []
        text = re.sub(r'\s+', ' ', text.strip())
        text = text.replace('#', '').replace('^3', '³').replace('^2', '²')            
        if '折' in text:
            text = self.parse_zhe(text, '折')
        elif '成' in text:
            text = self.parse_zhe(text, '成')
        if '=' not in text and '@' in text:
            # 可能是比较运算
            [left_part, right_part] = text.split('@')
            # @todo: 后续完善,需要单位换算
            right_values = self._get_left_source_value(right_part)
            if len(right_values) >= 2:
                result = self.solve(right_part)
                self.pre_steps = result.get('steps', [])
                self.target_value = result.get('result', None)
                target_unit = result.get('target_unit', None)
                text = f"{left_part}=@{target_unit}"
            elif len(right_values) == 1:
                target_unit = right_values[0].unit
                text = f"{left_part}=@{target_unit}"
            else:
                text = f"{left_part}=@"
        text = text.replace('＝', '=').replace('＠', '@').replace('?', '@').replace('个', '')
        ## 如果不包含@符号，添加兼容表达式：1元7角 => 1元7角=@角； 1元=@元
        if '@' not in text:
            target_unit = ''   # 默认取最后一个字符作为目标单位
            if text[-1] in unit_names:
                target_unit = text[-1]
            text += '=@' + target_unit
        if '%=' in text:
            text = text.replace('%=', '=').replace('%', '') + '百'
            step = ConversionStep(description="百分比转为小数等价于除以一百", operation="百分比转换为百单位计算", result="")
            self.add_pre_step(step)

        # 提取目标单位（@后面的单位）
        target_match = re.search(r'@([^=\s]+)', text)
        if not target_match:
            return UnitProblem(
                original_text=text,
                unit_type=UnitType.UNKNOWN,
                source_values=[],
                target_unit=""
            )
       
        target_unit = target_match.group(1)
        
        # 提取源数值和单位
        source_values = []
        
        # 先分离等号左边的部分
        left_part = text.split('=')[0].strip()
        # 提取源数值和单位
        source_values = self._get_left_source_value(left_part)
        if not source_values:
            raise ValueError(f"无法识别源数值和单位，原文：{text}")
        
        # 确定单位类型 - 优先根据目标单位确定类型
        unit_type = self._determine_unit_type_enhanced(source_values, target_unit)
        
        return UnitProblem(
            original_text=text,
            unit_type=unit_type,
            source_values=source_values,
            target_unit=target_unit
        )
    
    def _get_left_source_value(self, left_part: str) -> List[UnitValue]:
        """提取左侧的源数值和单位"""
        source_values = []
        # 如果左侧是可计算的数值表达式，直接计算表达式
        # 4.19+99.18 -> 104.37
        if re.match(r'^[\d\.\-]+[\+\-]+[\d\.\-]+$', left_part):
            try:
                # 计算表达式的值
                value = eval(left_part, {"__builtins__": None}, {})
                source_values.append(UnitValue(float(value), ""))  # 空单位表示纯数字
                return source_values
            except Exception as e:
                print(f"计算表达式失败：{e}")
        # 如果左侧是纯数字/小数/负数直接返回
        matches = []
        if re.match(r'^[\d\.\-]+$', left_part):
            value = float(left_part)
            source_values.append(UnitValue(value, ""))  # 空单位表示纯数字
            return source_values
        # 改进的正则表达式，更好地处理中文单位和复合单位
        # 匹配模式：数字+单位，其中单位可以是中文或英文
        patterns = [
            # 模式1: 处理像"58万"这样的简单单位
            r'(\d+(?:\.\d+)?)\s*([^\d\s@=]+?)(?=\d|$|=|@|\s)',
            # 模式2: 处理更复杂的情况
            r'(\d+(?:\.\d+)?)\s*([a-zA-Z\u4e00-\u9fff]+)',
            # 模式3: 最宽松的模式
            r'(\d+(?:\.\d+)?)\s*([^@=\d]+?)(?=\d|$|@|=)'
        ]
        matches = []
        for pattern in patterns:
            matches = re.findall(pattern, left_part)
            if matches:
                break
        if not matches:
            # 手动解析：处理纯数字情况（如 46600000=@万）
            print(f"正则表达式匹配失败，尝试手动解析：{left_part}")
            
            # 检查是否为纯数字（没有单位）
            pure_number_match = re.match(r'^(\d+(?:\.\d+)?)$', left_part.strip())
            if pure_number_match:
                # 纯数字情况，创建一个空单位的UnitValue
                value = float(pure_number_match.group(1))
                source_values.append(UnitValue(value, ""))  # 空单位表示纯数字
            else:
                # 尝试更宽松的解析
                # 分离数字和非数字部分
                number_part = re.search(r'([\d\.\-]+(?:\.\d+)?)', left_part)
                if number_part:
                    value = float(number_part.group(1))
                    # 提取单位部分（数字之后的所有非数字/非小数字符）
                    unit_part = re.sub(r'[\d\.\-]+(?:\.\d+)?', '', left_part).strip()
                    unit_part = unit_part.replace('=', '').replace('@', '').strip()
                    
                    if not unit_part:  # 如果没有单位，设为空字符串
                        unit_part = ""
                    
                    source_values.append(UnitValue(value, unit_part.rstrip('+')))
        else:
            # 正常的正则匹配成功
            for value_str, unit_str in matches:
                value = float(value_str)
                if unit_str[-1] == '-':
                    operator = '-'
                else:
                    operator = '+'
                # 清理单位字符串，移除可能的空白字符
                unit = unit_str.strip().rstrip('+-x').rstrip('=@')
                source_values.append(UnitValue(value, unit, operator))
        return source_values
    def _determine_unit_type_enhanced(self, source_values: List[UnitValue], target_unit: str) -> UnitType:
        """增强的单位类型确定方法，优先考虑目标单位"""
        # 首先检查目标单位的类型
        if target_unit in self.unit_type_mapping and target_unit != '分':
            return self.unit_type_mapping[target_unit]
        
        # 如果目标单位不在映射表中，检查源单位
        for value in source_values:
            if value.unit != '分' and value.unit in self.unit_type_mapping:
                return self.unit_type_mapping[value.unit]
        if target_unit == '分':
            return self.unit_type_mapping[target_unit]
        
        # 使用原有的逻辑作为备选
        all_values = source_values + [UnitValue(0, target_unit)]
        return self._determine_unit_type(all_values)
    
    def _determine_unit_type(self, values: List[UnitValue]) -> UnitType:
        """确定单位类型"""
        units = [v.unit for v in values if v.unit]  # 过滤空单位
        
        # 如果没有有效单位，检查是否有数字单位相关的目标单位
        if not units:
            # 从所有values中查找可能的单位信息
            all_units = [v.unit for v in values]
            if any(u in ["亿", "千万", "百万", "十万", "万", "千", "百"] for u in all_units):
                return UnitType.NUMBER
            # 默认返回数字类型（适用于纯数字换算）
            return UnitType.NUMBER
        
        # 优先检查明确的单位标识符
        # 货币单位优先级最高（因为有明确的元、角标识）
        if any(u in ["元", "角", "¥"] for u in units):
            return UnitType.CURRENCY
        
        # 时间单位（包括年、月、日等）
        if any(u in ["年", "月", "时", "秒", "小时", "h", "s", "min", "日", "天", "year", "month", "day"] for u in units):
            return UnitType.TIME
        
        # 长度单位
        if any(u in ["km", "千米", "公里", "m", "米", "dm", "分米", "cm", "厘米", "mm", "毫米"] for u in units):
            return UnitType.LENGTH
        
        # 质量单位
        if any(u in ["t", "吨", "kg", "千克", "公斤", "g", "克"] for u in units):
            return UnitType.MASS
        
        # 数字单位
        if any(u in ["亿", "千万", "百万", "十万", "万", "千", "百"] for u in units):
            return UnitType.NUMBER
        
        # 处理"分"的歧义
        if "分" in units:
            # 如果同时有其他时间单位，则认为是时间
            if any(u in ["年", "月", "时", "秒", "小时", "h", "s", "min", "日", "天"] for u in units):
                return UnitType.TIME
            # 如果同时有其他货币单位，则认为是货币
            elif any(u in ["元", "角", "¥"] for u in units):
                return UnitType.CURRENCY
            # 单独的"分"，根据上下文判断，默认为时间单位
            else:
                return UnitType.TIME
        
        # 如果都没有匹配到，尝试从映射表获取
        for value in values:
            if value.unit and value.unit in self.unit_type_mapping:
                unit_type = self.unit_type_mapping[value.unit]
                if unit_type:
                    return unit_type
        
        # 最后的备选：如果包含纯数字（空单位），很可能是数字单位换算
        if any(not v.unit for v in values):
            return UnitType.NUMBER
        
        raise ValueError(f"无法确定单位类型：{units}")
    
    def solve(self, text: str) -> Dict[str, Any]:
        """求解单位换算问题"""
        try:
            # 解析题目
            problem = self.parse_problem(text)
            
            # 找到匹配的算子
            calculator = self._find_calculator(problem)
            if not calculator:
                return {
                    'success': False,
                    'error': f'未找到适合的算子处理{problem.unit_type.value}类型',
                    'problem': text
                }
            
            # 求解
            result, steps = calculator.solve(problem)
            
            # 验证结果
            is_valid = calculator.validate_result(problem, result)
            
            # 收集所有使用的换算公式
            formulas_used = []
            for step in steps:
                if step.formula and step.formula not in formulas_used:
                    # 只收集标准的换算公式，排除计算过程描述
                    if "=" in step.formula and ("+" not in step.formula or "总" in step.formula):
                        formulas_used.append(step.formula)
            result = self.format_result(result)
            if self.pre_steps:
                steps = self.pre_steps + steps
            return {
                'success': True,
                'expression': text,
                'unit_type': problem.unit_type.value,
                'name': calculator.name,
                'description': calculator.description,  # 替换calculator字段
                'result': result,
                'result_unit': problem.target_unit,
                'steps': steps,
                'formula': "; ".join(formulas_used) if formulas_used else None,  # 新增综合公式字段
                'validation': is_valid,
                'source_values': [f"{v.value}{v.unit}" for v in problem.source_values],
                'target_value': self.target_value if hasattr(self, 'target_value') else None,
                'target_unit': problem.target_unit
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'problem': text
            }
    
    def _find_calculator(self, problem: UnitProblem) -> Optional[UnitCalculator]:
        """找到匹配的算子"""
        for calculator in self.calculators:
            if calculator.is_match_pattern(problem):
                return calculator
        return None
    
    def batch_solve(self, problems: List[str]) -> List[Dict[str, Any]]:
        """批量求解单位换算问题"""
        return [self.solve(problem) for problem in problems]
    
    def get_supported_units(self) -> Dict[str, List[str]]:
        """获取支持的单位类型"""
        result = {}
        for unit, unit_type in self.unit_type_mapping.items():
            type_name = unit_type.value
            if type_name not in result:
                result[type_name] = []
            result[type_name].append(unit)
        return result
