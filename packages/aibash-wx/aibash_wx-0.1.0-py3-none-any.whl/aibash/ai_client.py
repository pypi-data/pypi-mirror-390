"""
AI 模型客户端模块

支持 OpenAI API 和 Ollama 本地模型
"""

import os
import json
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AIClient:
    """AI 客户端"""
    
    def __init__(
        self,
        api_base: str,
        api_key: str,
        model_name: str,
        provider: str = "openai"
    ):
        """
        初始化 AI 客户端
        
        Args:
            api_base: API 基础 URL
            api_key: API 密钥
            model_name: 模型名称
            provider: 提供商 (openai 或 ollama)
        """
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.provider = provider.lower()
        
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
    
    def generate_command(self, prompt: str, timeout: int = 30) -> str:
        """
        生成命令
        
        Args:
            prompt: 提示词
            timeout: 超时时间（秒）
            
        Returns:
            生成的命令
            
        Raises:
            Exception: 如果生成失败
        """
        if self.provider == "ollama":
            return self._generate_with_ollama(prompt, timeout)
        else:
            return self._generate_with_openai(prompt, timeout)
    
    def _generate_with_openai(self, prompt: str, timeout: int) -> str:
        """使用 OpenAI API 生成命令"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
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
                raise Exception("AI 返回空内容")
            
            # 清理输出，只保留命令
            command = self._extract_command(content)
            return command
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {e}")
        except Exception as e:
            raise Exception(f"生成命令失败: {e}")
    
    def _generate_with_ollama(self, prompt: str, timeout: int) -> str:
        """使用 Ollama API 生成命令"""
        # 尝试使用 OpenAI 兼容的 API（Ollama 0.1.16+）
        openai_compat_url = f"{self.api_base}/v1/chat/completions"
        
        try:
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = self.session.post(
                openai_compat_url,
                json=data,
                timeout=timeout
            )
            
            # 如果 OpenAI 兼容 API 可用，使用它
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return self._extract_command(content)
        except Exception:
            pass  # 回退到传统 API
        
        # 使用传统的 Ollama API
        url = f"{self.api_base}/api/generate"
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 500
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
                raise Exception("AI 返回空内容")
            
            # 清理输出，只保留命令
            command = self._extract_command(content)
            return command
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API 请求失败: {e}")
        except Exception as e:
            raise Exception(f"生成命令失败: {e}")
    
    def _extract_command(self, content: str) -> str:
        """
        从 AI 输出中提取命令
        
        Args:
            content: AI 返回的内容
            
        Returns:
            提取的命令
        """
        # 移除代码块标记
        content = content.strip()
        
        # 移除 markdown 代码块
        if content.startswith("```"):
            lines = content.split("\n")
            # 跳过第一行（```bash 或 ```）
            if len(lines) > 1:
                content = "\n".join(lines[1:])
            # 移除最后的 ```
            if content.endswith("```"):
                content = content[:-3]
        
        # 移除前后空白
        content = content.strip()
        
        # 只取第一行（命令应该是单行的）
        lines = content.split("\n")
        command = lines[0].strip()
        
        # 移除可能的 $ 或 > 提示符
        command = command.lstrip("$").lstrip(">").strip()
        
        return command
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            是否连接成功
        """
        try:
            if self.provider == "ollama":
                # Ollama 测试连接
                url = f"{self.api_base}/api/tags"
                response = self.session.get(url, timeout=5)
                return response.status_code == 200
            else:
                # OpenAI API 测试连接（简单请求）
                url = f"{self.api_base}/models"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = self.session.get(url, headers=headers, timeout=5)
                return response.status_code == 200
        except Exception:
            return False

