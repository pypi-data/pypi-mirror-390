"""
配置管理模块

处理用户配置，包括模型连接、密钥、系统信息等
"""

import os
import yaml
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    """模型配置"""
    api_base: str = "https://api.openai.com/v1"
    api_key: str = ""
    model_name: str = "gpt-3.5-turbo"
    provider: str = "openai"  # openai 或 ollama


@dataclass
class HistoryConfig:
    """历史记录配置"""
    enabled: bool = True
    max_records: int = 50
    include_output: bool = True
    history_file: str = ""


@dataclass
class AutomationConfig:
    """自动化模式配置"""
    auto_confirm_all: bool = False
    auto_confirm_commands: bool = False
    auto_confirm_files: bool = False
    auto_confirm_web: bool = False
    max_steps: int = 30
    allow_silence: bool = True
    enable_auto_summary: bool = False
    summary_workers: int = 4


@dataclass
class AppConfig:
    """应用配置"""
    model: ModelConfig = None
    history: HistoryConfig = None
    automation: AutomationConfig = None
    system_info: str = ""
    custom_prompt: str = ""
    use_default_prompt: bool = True
    model_params: dict = None  # temperature, max_tokens, timeout 等
    ui: dict = None  # enable_colors, single_key_mode 等
    
    def __post_init__(self):
        if self.model is None:
            self.model = ModelConfig()
        if self.history is None:
            self.history = HistoryConfig()
        if self.automation is None:
            self.automation = AutomationConfig()
        if self.model_params is None:
            self.model_params = {}
        if self.ui is None:
            self.ui = {}


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            config_dir = Path.home() / ".aibash"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._ensure_defaults()
    
    def _load_config(self) -> AppConfig:
        """加载配置文件"""
        if not self.config_path.exists():
            return AppConfig()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # 解析配置
            model_data = data.get('model', {})
            model_config = ModelConfig(
                api_base=model_data.get('api_base', 'https://api.openai.com/v1'),
                api_key=model_data.get('api_key', ''),
                model_name=model_data.get('model_name', 'gpt-3.5-turbo'),
                provider=model_data.get('provider', 'openai')
            )
            
            history_data = data.get('history', {})
            history_config = HistoryConfig(
                enabled=history_data.get('enabled', True),
                max_records=history_data.get('max_records', 50),
                include_output=history_data.get('include_output', True),
                history_file=history_data.get('history_file', '')
            )
            
            automation_data = data.get('automation', {})
            automation_config = AutomationConfig(
                auto_confirm_all=automation_data.get('auto_confirm_all', False),
                auto_confirm_commands=automation_data.get('auto_confirm_commands', False),
                auto_confirm_files=automation_data.get('auto_confirm_files', False),
                auto_confirm_web=automation_data.get('auto_confirm_web', False),
                max_steps=automation_data.get('max_steps', 30),
                allow_silence=automation_data.get('allow_silence', True),
                enable_auto_summary=automation_data.get('enable_auto_summary', False),
                summary_workers=automation_data.get('summary_workers', 4),
            )
            
            # 获取系统信息
            system_info = data.get('system_info', '')
            if not system_info:
                system_info = self._get_default_system_info()
            
            return AppConfig(
                model=model_config,
                history=history_config,
                automation=automation_config,
                system_info=system_info,
                custom_prompt=data.get('custom_prompt', ''),
                use_default_prompt=data.get('use_default_prompt', True),
                model_params=data.get('model_params', {}),
                ui=data.get('ui', {})
            )
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}, using default configuration")
            return AppConfig()
    
    def _ensure_defaults(self):
        """确保默认值设置"""
        if not self.config.system_info:
            self.config.system_info = self._get_default_system_info()
        
        if not self.config.history.history_file:
            config_dir = self.config_path.parent
            self.config.history.history_file = str(config_dir / "history.json")
        
        # UI 默认参数
        self.config.ui.setdefault('enable_colors', True)
        self.config.ui.setdefault('single_key_mode', True)
        self.config.ui.setdefault('language', 'en')
        
        # 自动化默认参数
        if not isinstance(self.config.automation, AutomationConfig):
            self.config.automation = AutomationConfig(
                auto_confirm_all=self.config.automation.get('auto_confirm_all', False),
                auto_confirm_commands=self.config.automation.get('auto_confirm_commands', False),
                auto_confirm_files=self.config.automation.get('auto_confirm_files', False),
                auto_confirm_web=self.config.automation.get('auto_confirm_web', False),
                max_steps=self.config.automation.get('max_steps', 20),
            )
        else:
            if self.config.automation.max_steps <= 0:
                self.config.automation.max_steps = 30
            if self.config.automation.summary_workers <= 0:
                self.config.automation.summary_workers = 4
    
    def _get_default_system_info(self) -> str:
        """获取默认系统信息"""
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        return f"{system} {release} ({machine})"
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_dict = {
                'model': asdict(self.config.model),
                'history': asdict(self.config.history),
                'automation': asdict(self.config.automation),
                'system_info': self.config.system_info,
                'custom_prompt': self.config.custom_prompt,
                'use_default_prompt': self.config.use_default_prompt,
                'model_params': self.config.model_params,
                'ui': self.config.ui
            }
            
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to save config file: {e}")
    
    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self.config
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            # 支持嵌套属性，如 model__api_key
            if '__' in key:
                parts = key.split('__', 1)
                obj_name = parts[0]
                attr_name = parts[1]
                
                if obj_name == 'model' and hasattr(self.config.model, attr_name):
                    setattr(self.config.model, attr_name, value)
                elif obj_name == 'history' and hasattr(self.config.history, attr_name):
                    setattr(self.config.history, attr_name, value)
                elif obj_name == 'automation' and hasattr(self.config.automation, attr_name):
                    setattr(self.config.automation, attr_name, value)
            elif hasattr(self.config, key):
                setattr(self.config, key, value)
            elif hasattr(self.config.model, key):
                setattr(self.config.model, key, value)
            elif hasattr(self.config.history, key):
                setattr(self.config.history, key, value)
            elif hasattr(self.config.automation, key):
                setattr(self.config.automation, key, value)
        self._ensure_defaults()

