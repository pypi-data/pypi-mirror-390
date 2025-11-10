"""
Agent Builder - 工厂模式创建 Agent
"""

from typing import Optional
from ..interfaces.ai_agent import AIAgent
from ..config import ModelConfig
from .openai_agent import OpenAIAgent
from .ollama_agent import OllamaAgent


class AgentBuilder:
    """Agent 构建器"""
    
    @staticmethod
    def build_agent(config: ModelConfig, **kwargs) -> Optional[AIAgent]:
        """
        根据配置构建 Agent
        
        Args:
            config: 模型配置
            **kwargs: 额外参数（temperature, max_tokens, timeout）
            
        Returns:
            AIAgent 实例
        """
        provider = config.provider.lower()
        
        if provider == "openai":
            return OpenAIAgent(
                api_base=config.api_base,
                api_key=config.api_key,
                model_name=config.model_name,
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 500),
                timeout=kwargs.get('timeout', 30)
            )
        elif provider == "ollama":
            return OllamaAgent(
                api_base=config.api_base,
                model_name=config.model_name,
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 500),
                timeout=kwargs.get('timeout', 30)
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

