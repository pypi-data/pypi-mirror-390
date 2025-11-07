from openai import OpenAI
import json
import re
import os
from typing import Optional, Dict, Any

from kousuan.skills import SmartCalculatorEngine

default_system_prompt = """
你是一名小学数学老师，请为小学生提供的口算题目生成详细的分步解题过程.

## 要求
1. 选择符合小学生认知水平的的计算方法进行解题。优先提供最有效的解题技巧。
2. 提供分步骤的解题步骤，每个步骤包含中文的描述 `description` 和操作说明 `operation`。
3. 确保计算结果正确，合理的参考题目的提示答案或解题步骤信息。
4. 输出的JSON中，尽量包含每一步的公式（如有）。

## 话题边界
1. 仅限于数学问题，其它学科拒绝回答，直接拒绝回答。
2. 输出的文字描述内容不允许使用政治、宗教、暴力等敏感词汇。

## 输出格式要求
- 并输出结构化JSON，请严格输出JSON格式，不要输出多余内容。
- 方法名称name，保持简洁明了不添加修饰词，如果提供了参考计算技巧，请保持与参考计算技巧名称保持一致。
- 字段包括：question, name, description, result, steps, error。每个step包含description, operation, result, formula（如有）。
- `formula`公式是可以简洁描述计算技巧的或数理论说明。计算步骤中的公式可选。
- description字段是对该步骤的简要描述, 描述不超过30个字。注意步骤中的描述、操作和公式要与解题过程一致，并且内容不要重复。

=== 参考输出格式
{
  "question": "47x53",
  "name": "中间数乘法",
  "description": "对称分布数相乘，中数平方减差平方",
  "formula": "(M-x)(M+x) = M² - x²",
  "result": 2491,
  "steps": [
    {
      "description": "使用中间数乘法：47 × 53",
      "operation": "识别模式",
      "result": "寻找中间数进行对称分解,确定中间数为50，差值为3",
    },
    {
      "description": "计算：50² - 3² = 2500 - 9 = 2491",
      "operation": "计算结果",
      "result": 2491,
      "formula": "(M-x)(M+x) = M² - x²"
    }
  ],
  "error": null
}
"""

class AICalculator:
    """AI计算器类，用于生成口算题目的解题建议"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, 
                 model: str = "gpt-5-mini", temperature: float = 0.4, max_tokens: int = 1500):
        """
        初始化AI计算器
        
        Args:
            api_key: OpenAI API密钥，默认从环境变量获取
            base_url: API基础URL，默认从环境变量获取
            model: 使用的模型名称
            temperature: 生成温度
            max_tokens: 最大生成token数
        """
        env = os.environ
        self.api_key = api_key or env.get("OPENAI_API_KEY", "")
        self.base_url = base_url or env.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 初始化客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # 系统提示词
        self.system_prompt = default_system_prompt
    
    def generate(self, prompt: str, user_input: str = '', format: str = "json") -> Any:
        """
        生成AI响应
        
        Args:
            prompt: 系统提示词
            user_input: 用户输入
            format: 返回格式，支持 "json" 或 "text"
            
        Returns:
            生成的响应内容
        """
        try:
            messages = [
                {"role": "system", "content": prompt}
            ]
            if user_input:
                messages.append({"role": "user", "content": user_input})
                
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            content = response.choices[0].message.content
            if not content:
                return {"success": False, "error": "LLM未返回内容"}
            

            if format == "json":
                think_content = ""
                index_think = content.find('</think>')
                if index_think != -1:
                    think_content = content[:index_think]
                    ## 提取<think></think>标签中的内容
                    think_content = think_content.lstrip('<think>').strip()
                    content = content[index_think:]
                content = content.replace('```json', '').replace('```', '')
                json_data = json.loads(content.strip())
                if think_content:
                    json_data['think'] = think_content.strip()
                return json_data
            return content.strip()
        except Exception as e:
            print(f"Error during AI generation: {e}")
            return {"success": False, "error": str(e)}

    def resolve_question(self, question: str, calc_skills: Optional[str] = None) -> Dict[str, Any]:
        """
        生成计算建议
        
        Args:
            question: 口算题目
            calc_skills: 参考计算技巧（可选）
            
        Returns:
            包含解题建议的字典
        """
        user_input = f"""题目：{question}"""
        if calc_skills:
            user_input += f"\n## 参考计算技巧：\n\n{calc_skills}"
            
        result = self.generate(self.system_prompt, user_input=user_input, format="json")
        
        if isinstance(result, dict) and result.get("steps"):
            result['expression'] = question
            result['success'] = True
        else:
            result = {
                "success": False,
                "error": "未能生成有效的解题建议"
            }
        return result