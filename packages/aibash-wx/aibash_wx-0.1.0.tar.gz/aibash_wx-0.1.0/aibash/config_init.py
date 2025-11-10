"""
配置初始化工具

帮助用户快速创建和配置 AIBash
"""

import os
import sys
from pathlib import Path
from .config import ConfigManager


def init_config_interactive():
    """交互式初始化配置"""
    print("=" * 60)
    print("AIBash Configuration Initialization")
    print("=" * 60)
    print()
    
    # 选择提供商
    print("Please select AI model provider:")
    print("  1. OpenAI API")
    print("  2. Ollama (Local)")
    
    while True:
        choice = input("Enter option (1/2): ").strip()
        if choice == "1":
            provider = "openai"
            break
        elif choice == "2":
            provider = "ollama"
            break
        else:
            print("Invalid option, please try again")
    
    # 配置模型信息
    if provider == "openai":
        api_base = input("API Base URL [https://api.openai.com/v1]: ").strip()
        if not api_base:
            api_base = "https://api.openai.com/v1"
        
        api_key = input("API Key (required): ").strip()
        if not api_key:
            print("Error: API Key cannot be empty")
            return False
        
        model_name = input("Model name [gpt-3.5-turbo]: ").strip()
        if not model_name:
            model_name = "gpt-3.5-turbo"
    else:  # ollama
        api_base = input("Ollama API Base URL [http://localhost:11434]: ").strip()
        if not api_base:
            api_base = "http://localhost:11434"
        
        api_key = ""
        
        model_name = input("Model name [llama2]: ").strip()
        if not model_name:
            model_name = "llama2"
    
    # 历史记录配置
    print("\nHistory configuration:")
    history_enabled = input("Enable history? (Y/n): ").strip().lower()
    history_enabled = history_enabled != "n"
    
    if history_enabled:
        max_records = input("Max records [50]: ").strip()
        max_records = int(max_records) if max_records.isdigit() else 50
        
        include_output = input("Include command output? (Y/n): ").strip().lower()
        include_output = include_output != "n"
    else:
        max_records = 50
        include_output = True
    
    # 系统信息
    print("\nSystem information configuration:")
    system_info = input("System info (leave empty for auto-detection): ").strip()
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 更新配置
    config_manager.update_config(
        model__provider=provider,
        model__api_base=api_base,
        model__api_key=api_key,
        model__model_name=model_name,
        history__enabled=history_enabled,
        history__max_records=max_records,
        history__include_output=include_output
    )
    
    # 设置系统信息（如果用户提供了）
    if system_info:
        config_manager.update_config(system_info=system_info)
    
    # 保存配置
    try:
        config_manager.save_config()
        print("\n✓ Configuration saved to:", config_manager.config_path)
        return True
    except Exception as e:
        print(f"\n✗ Failed to save configuration: {e}")
        return False


def main():
    """主函数"""
    try:
        success = init_config_interactive()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

