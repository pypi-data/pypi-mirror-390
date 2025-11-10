"""
AIBash 主程序入口

处理命令行参数和核心逻辑
"""

import sys
import argparse
from typing import Optional

from .config import ConfigManager
from .agents.agent_builder import AgentBuilder
from .history import HistoryManager
from .interactive import InteractiveSelector
from .prompt import PromptManager
from .utils.terminal import TerminalOutput
from . import config_init


class AIBash:
    """AIBash 主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 AIBash
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化历史记录管理器
        self.history_manager = HistoryManager(
            history_file=self.config.history.history_file,
            max_records=self.config.history.max_records,
            enabled=self.config.history.enabled
        )
        
        # 初始化终端输出
        self.terminal = TerminalOutput(enable_colors=self.config.ui.get('enable_colors', True))
        
        # 初始化交互式选择器
        self.interactive = InteractiveSelector(
            enable_colors=self.config.ui.get('enable_colors', True)
        )
        
        # 初始化 AI Agent
        self.agent = None
        self._init_agent()
    
    def _init_agent(self):
        """初始化 AI Agent"""
        model_config = self.config.model
        if not model_config.api_key and model_config.provider == "openai":
            self.terminal.warning("Warning: API key not configured, please configure it first")
            return
        
        try:
            self.agent = AgentBuilder.build_agent(
                model_config,
                temperature=self.config.model_params.get('temperature', 0.3),
                max_tokens=self.config.model_params.get('max_tokens', 500),
                timeout=self.config.model_params.get('timeout', 30)
            )
        except Exception as e:
            self.terminal.error(f"Failed to initialize AI Agent: {e}")
    
    def generate_command(self, user_query: str) -> Optional[str]:
        """
        生成命令
        
        Args:
            user_query: 用户查询
            
        Returns:
            生成的命令，如果失败则返回 None
        """
        if not self.agent:
            self.terminal.error("Error: AI Agent not initialized, please check configuration")
            return None
        
        # 准备历史上下文
        history_context = ""
        if self.config.history.enabled and self.config.history.include_output:
            recent_records = self.history_manager.get_recent_records(10)
            history_context = PromptManager.format_history_context(recent_records)
        
        # 格式化 prompt
        prompt = PromptManager.format_prompt(
            user_query=user_query,
            system_info=self.config.system_info,
            history_context=history_context,
            custom_prompt=self.config.custom_prompt if not self.config.use_default_prompt else ""
        )
        
        try:
            self.terminal.info("Generating command...")
            command = self.agent.generate_command(prompt)
            return command
        except Exception as e:
            self.terminal.error(f"Error: Failed to generate command - {e}")
            return None
    
    def process_query(self, user_query: str):
        """
        处理用户查询
        
        Args:
            user_query: 用户查询
        """
        # 生成命令
        command = self.generate_command(user_query)
        if not command:
            return
        
        # 交互式选择
        single_key_mode = self.config.ui.get('single_key_mode', True)
        
        while True:
            self.interactive.show_command(command)
            self.interactive.show_options(single_key_mode=single_key_mode)
            
            choice = self.interactive.get_user_choice(single_key_mode=single_key_mode)
            if not choice:
                self.terminal.warning("Invalid option, please try again")
                continue
            
            if choice == 'help':
                self.interactive.show_help()
                continue
            
            if choice == 'skip':
                self.terminal.info("Command execution cancelled")
                return
            
            if choice == 'copy':
                self.interactive.copy_to_clipboard(command)
                continue
            
            if choice == 'modify':
                modified_command = self.interactive.get_modified_command(command)
                if modified_command:
                    command = modified_command
                continue
            
            if choice == 'execute':
                success, output = self.interactive.execute_command(command)
                
                # 保存历史记录
                if self.config.history.enabled:
                    self.history_manager.add_record(
                        command=command,
                        output=output if self.config.history.include_output else "",
                        success=success,
                        user_query=user_query
                    )
                
                return


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='aibash',
        description='AI-powered shell command generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aibash -l "list all files in current directory"
  aibash -l "find files containing test"
  aibash --config /path/to/config.yaml -l "perform some operation"

For more information, visit: https://github.com/W1412X/aibash
        """
    )
    
    parser.add_argument(
        '-l', '--lang',
        dest='query',
        metavar='QUERY',
        help='Natural language description to generate shell command'
    )
    
    parser.add_argument(
        '--config',
        metavar='PATH',
        help='Specify config file path (default: ~/.aibash/config.yaml)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Interactive configuration initialization'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='View command execution history'
    )
    
    parser.add_argument(
        '--clear-history',
        action='store_true',
        help='Clear command execution history'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test AI connection'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 如果是初始化配置
    if args.init:
        config_init.main()
        return
    
    # 创建 AIBash 实例（用于历史记录和测试）
    try:
        aibash = AIBash(config_path=args.config)
    except Exception as e:
        print(f"Error: Initialization failed - {e}", file=sys.stderr)
        sys.exit(1)
    
    # 查看历史记录
    if args.history:
        history_records = aibash.history_manager.load_records()
        if not history_records:
            print("No history records")
        else:
            print(f"\nTotal {len(history_records)} history records:\n")
            print("=" * 80)
            for i, record in enumerate(history_records[-20:], 1):  # 显示最近20条
                timestamp = record.get('timestamp', '')
                user_query = record.get('user_query', '')
                command = record.get('command', '')
                success = record.get('success', True)
                output = record.get('output', '')
                
                print(f"\n[{i}] {timestamp}")
                if user_query:
                    print(f"  Query: {user_query}")
                print(f"  Command: {command}")
                print(f"  Status: {'✓ Success' if success else '✗ Failed'}")
                if output:
                    output_preview = output[:100] + "..." if len(output) > 100 else output
                    print(f"  Output: {output_preview}")
                print("-" * 80)
        return
    
    # 清空历史记录
    if args.clear_history:
        confirm = input("Are you sure you want to clear all history records? (y/N): ").strip().lower()
        if confirm == 'y':
            aibash.history_manager.clear_history()
            print("✓ History records cleared")
        else:
            print("Operation cancelled")
        return
    
    # 测试连接
    if args.test:
        if not aibash.agent:
            aibash.terminal.error("Error: AI Agent not initialized")
            aibash.terminal.info("Please run 'aibash --init' to configure first")
            sys.exit(1)
        
        aibash.terminal.info("Testing AI connection...")
        if aibash.agent.test_connection():
            aibash.terminal.success("✓ Connection successful")
            model_info = aibash.agent.get_model_info()
            aibash.terminal.info(f"Model: {model_info.get('model', 'N/A')}")
            aibash.terminal.info(f"Provider: {model_info.get('provider', 'N/A')}")
        else:
            aibash.terminal.error("✗ Connection failed, please check configuration and network connection")
        return
    
    # 如果没有提供查询，显示帮助
    if not args.query:
        parser.print_help()
        return
    
    # 检查 AI Agent 是否初始化
    if not aibash.agent:
        aibash.terminal.error("\nError: AI Agent not initialized")
        aibash.terminal.info("Please run 'aibash --init' to configure, or check configuration file")
        sys.exit(1)
    
    try:
        aibash.process_query(args.query)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        if '--debug' in sys.argv:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

