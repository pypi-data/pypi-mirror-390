"""
配置初始化工具

帮助用户快速创建和配置 AIBash
"""

import sys
from .config import ConfigManager
from .i18n import I18n, t


def init_config_interactive():
    """交互式初始化配置"""
    print("=" * 60)
    language = input(t("config_init_language_prompt")).strip().lower() or "en"
    if language not in ("en", "zh"):
        language = "en"
    I18n.set_language(language)
    print(t("config_init_title"))
    print("=" * 60)
    print()
    
    # 选择提供商
    print(t("config_init_provider_prompt"))
    print(t("config_init_option_openai"))
    print(t("config_init_option_ollama"))
    
    while True:
        choice = input(t("config_init_input_option")).strip()
        if choice == "1":
            provider = "openai"
            break
        elif choice == "2":
            provider = "ollama"
            break
        else:
            print(t("common_invalid_option"))
    
    # 配置模型信息
    if provider == "openai":
        print(t("config_init_openai_tips"))
        default_base = "https://api.openai.com/v1"
        api_base = input(t("config_init_api_base", default=default_base)).strip()
        if not api_base:
            api_base = default_base
        
        api_key = input(t("config_init_api_key")).strip()
        if not api_key:
            print(t("config_init_error_no_key"))
            return False
        
        default_model = "gpt-3.5-turbo"
        model_name = input(t("config_init_model", default=default_model)).strip()
        if not model_name:
            model_name = default_model
    else:  # ollama
        default_base = "http://localhost:11434"
        api_base = input(t("config_init_api_base", default=default_base)).strip()
        if not api_base:
            api_base = default_base
        
        api_key = ""
        
        default_model = "llama2"
        model_name = input(t("config_init_model", default=default_model)).strip()
        if not model_name:
            model_name = default_model
    
    # 历史记录配置
    print(t("config_init_history_header"))
    history_enabled = input(t("config_init_history_enabled")).strip().lower()
    history_enabled = history_enabled != "n"
    
    if history_enabled:
        max_records = input(t("config_init_history_max")).strip()
        max_records = int(max_records) if max_records.isdigit() else 50
        
        include_output = input(t("config_init_history_output")).strip().lower()
        include_output = include_output != "n"
    else:
        max_records = 50
        include_output = True
    
    # 系统信息
    print(t("config_init_system_header"))
    system_info = input(t("config_init_system_info")).strip()
    
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
    config_manager.config.ui['language'] = language
    
    # 设置系统信息（如果用户提供了）
    if system_info:
        config_manager.update_config(system_info=system_info)
    
    # 保存配置
    try:
        config_manager.save_config()
        print(t("config_init_save_success", path=config_manager.config_path))
        return True
    except Exception as e:
        print(t("config_init_save_failed", error=e))
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

