"""
Agent 实现 - OpenAI
"""

from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..interfaces.ai_agent import AIAgent


class OpenAIAgent(AIAgent):
    """OpenAI API Agent"""
    
    def __init__(
        self,
        api_base: str,
        api_key: str,
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
        timeout: int = 30
    ):
        """
        初始化 OpenAI Agent
        
        Args:
            api_base: API 基础 URL
            api_key: API 密钥
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            timeout: 超时时间
        """
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # 创建带重试的 session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def generate_command(self, prompt: str, **kwargs) -> str:
        """生成命令"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        timeout = kwargs.get('timeout', self.timeout)
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        expect_raw = kwargs.get('expect_raw', False)
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                raise Exception("AI returned empty content")
            
            if expect_raw:
                return content.strip()
            
            return self._extract_command(content)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to generate command: {e}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            url = f"{self.api_base}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = self.session.get(url, headers=headers, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "openai",
            "model": self.model_name,
            "api_base": self.api_base
        }
    
    def _extract_command(self, content: str) -> str:
        """从 AI 输出中提取命令"""
        content = content.strip()
        
        # 移除 markdown 代码块
        if content.startswith("```"):
            lines = content.split("\n")
            if len(lines) > 1:
                content = "\n".join(lines[1:])
            if content.endswith("```"):
                content = content[:-3]
        
        content = content.strip()
        lines = content.split("\n")
        command = lines[0].strip()
        command = command.lstrip("$").lstrip(">").strip()
        
        return command

