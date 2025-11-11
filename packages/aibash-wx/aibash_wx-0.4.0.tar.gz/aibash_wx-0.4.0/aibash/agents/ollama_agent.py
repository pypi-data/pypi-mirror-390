"""
Agent 实现 - Ollama
"""

from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..interfaces.ai_agent import AIAgent


class OllamaAgent(AIAgent):
    """Ollama API Agent"""
    
    def __init__(
        self,
        api_base: str,
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
        timeout: int = 30
    ):
        """
        初始化 Ollama Agent
        
        Args:
            api_base: API 基础 URL
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            timeout: 超时时间
        """
        self.api_base = api_base.rstrip('/')
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
        # 优先尝试 OpenAI 兼容 API
        openai_compat_url = f"{self.api_base}/v1/chat/completions"
        
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        timeout = kwargs.get('timeout', self.timeout)
        expect_raw = kwargs.get('expect_raw', False)
        
        try:
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = self.session.post(
                openai_compat_url,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    if expect_raw:
                        return content.strip()
                    return self._extract_command(content)
        except Exception:
            pass  # 回退到传统 API
        
        # 使用传统 Ollama API
        url = f"{self.api_base}/api/generate"
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = self.session.post(
                url,
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result.get("response", "")
            
            if not content:
                raise Exception("AI returned empty content")
            
            if expect_raw:
                return content.strip()
            
            return self._extract_command(content)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to generate command: {e}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            # 检查模型是否存在
            url = f"{self.api_base}/api/tags"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return self.model_name in model_names
            return False
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "ollama",
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

