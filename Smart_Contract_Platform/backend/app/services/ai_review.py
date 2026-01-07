"""
AI合同审查服务
使用DeepSeek API和RAG进行合同条款审查
"""
import json
import httpx
from typing import List, Dict, Optional
from app.core.config import settings
from app.services.rag_service import get_rag_service


class AIReviewService:
    """AI合同审查服务类"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.api_base = settings.deepseek_api_base
        self.model = settings.deepseek_model
        self.rag_service = get_rag_service()
    
    def build_review_prompt(self, contract_clauses: str, relevant_laws: List[Dict]) -> str:
        """构建审查提示词"""
        # 构建相关法律条款上下文
        law_context = ""
        if relevant_laws:
            law_context = "相关法律条款参考：\n\n"
            for i, law in enumerate(relevant_laws, 1):
                law_context += f"{i}. {law['content']}\n"
                if law.get('metadata', {}).get('source_file'):
                    law_context += f"   来源：{law['metadata']['source_file']}\n"
                law_context += "\n"
        
        prompt = f"""你是一位专业的合同审查专家。请仔细审查以下合同条款，并基于提供的相关法律条款，标出所有问题、风险点和改进建议。

{law_context}

待审查的合同条款：
{contract_clauses}

请按照以下JSON格式返回审查结果：
{{
    "issues": [
        {{
            "type": "风险/违规/不完善",
            "severity": "高/中/低",
            "location": "具体位置描述（如：第3条、第5款等）",
            "description": "问题详细描述",
            "suggestion": "具体改进建议"
        }}
    ],
    "suggestions": [
        "总体改进建议1",
        "总体改进建议2"
    ],
    "compliance_score": 85.5,
    "reviewed_sections": ["已审查的条款片段列表"]
}}

要求：
1. 仔细分析合同条款，识别所有潜在的法律风险、违规问题和需要完善的地方
2. 根据相关法律条款，提供准确的合规性判断
3. 为每个问题提供具体的改进建议
4. 给出0-100的合规性评分
5. 只返回JSON格式，不要添加其他说明文字
"""
        return prompt
    
    def call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        if not self.api_key:
            raise Exception("DeepSeek API密钥未配置，请在.env文件中设置DEEPSEEK_API_KEY")
        
        url = f"{self.api_base}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的合同审查专家，擅长分析合同条款的合规性和风险点。请严格按照JSON格式返回审查结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API返回格式异常: {result}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"DeepSeek API调用失败: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"DeepSeek API调用错误: {str(e)}")
    
    def parse_review_result(self, api_response: str) -> Dict:
        """解析API返回的审查结果"""
        try:
            # 尝试提取JSON部分（可能包含markdown代码块）
            json_str = api_response.strip()
            
            # 移除可能的markdown代码块标记
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            elif json_str.startswith("```"):
                json_str = json_str[3:]
            
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            json_str = json_str.strip()
            
            # 解析JSON
            result = json.loads(json_str)
            
            # 验证和规范化结果
            if "issues" not in result:
                result["issues"] = []
            elif not isinstance(result["issues"], list):
                result["issues"] = []
            
            # 确保每个issue都有必需的字段
            for issue in result["issues"]:
                if not isinstance(issue, dict):
                    continue
                if "type" not in issue:
                    issue["type"] = "不完善"
                if "severity" not in issue:
                    issue["severity"] = "中"
                if "location" not in issue:
                    issue["location"] = "未知位置"
                if "description" not in issue:
                    issue["description"] = ""
                if "suggestion" not in issue:
                    issue["suggestion"] = ""
            
            if "suggestions" not in result:
                result["suggestions"] = []
            elif not isinstance(result["suggestions"], list):
                result["suggestions"] = []
            
            if "compliance_score" not in result:
                result["compliance_score"] = 0.0
            else:
                # 确保评分在0-100范围内
                result["compliance_score"] = max(0.0, min(100.0, float(result["compliance_score"])))
            
            if "reviewed_sections" not in result:
                result["reviewed_sections"] = []
            elif not isinstance(result["reviewed_sections"], list):
                result["reviewed_sections"] = []
            
            return result
        except json.JSONDecodeError as e:
            # 如果JSON解析失败，尝试提取关键信息
            raise Exception(f"无法解析AI返回的JSON格式结果: {str(e)}\n原始响应: {api_response[:500]}")
    
    def review_contract(self, contract_clauses: str) -> Dict:
        """审查合同条款"""
        if not contract_clauses or not contract_clauses.strip():
            return {
                "issues": [],
                "suggestions": ["合同条款为空，无法进行审查"],
                "compliance_score": 0.0,
                "reviewed_sections": [],
                "error": "合同条款为空"
            }
        
        try:
            # 1. 使用RAG检索相关法律条款
            relevant_laws = self.rag_service.search_relevant_chunks(
                query=contract_clauses,
                top_k=5
            )
            
            # 2. 构建提示词
            prompt = self.build_review_prompt(contract_clauses, relevant_laws)
            
            # 3. 调用DeepSeek API
            api_response = self.call_deepseek_api(prompt)
            
            # 4. 解析结果
            result = self.parse_review_result(api_response)
            
            # 5. 添加元数据
            result["relevant_laws_count"] = len(relevant_laws)
            result["reviewed_at"] = None  # 可以在调用时添加时间戳
            
            return result
        except Exception as e:
            # 返回错误信息
            return {
                "issues": [],
                "suggestions": [],
                "compliance_score": 0.0,
                "reviewed_sections": [],
                "error": str(e)
            }


# 全局AI审查服务实例
_ai_review_service: Optional[AIReviewService] = None

def get_ai_review_service() -> AIReviewService:
    """获取AI审查服务实例（单例模式）"""
    global _ai_review_service
    if _ai_review_service is None:
        _ai_review_service = AIReviewService()
    return _ai_review_service

