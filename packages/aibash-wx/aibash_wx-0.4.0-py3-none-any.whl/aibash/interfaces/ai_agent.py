"""
AI Agent 接口定义

定义统一的 AI Agent 接口，支持多种 AI 提供商
"""

from abc import ABC, abstractmethod
from typing import Optional


class AIAgent(ABC):
    """AI Agent 抽象基类"""
    
    @abstractmethod
    def generate_command(self, prompt: str, **kwargs) -> str:
        """
        生成命令
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
                expect_raw: bool - 当为 True 时返回模型原始输出（不做命令提取）
            
        Returns:
            生成的命令
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            是否连接成功
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        pass

