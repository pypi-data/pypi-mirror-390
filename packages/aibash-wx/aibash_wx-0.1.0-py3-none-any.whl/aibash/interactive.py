"""
交互式命令选择模块

提供用户交互界面，让用户选择执行/修改/放弃命令
支持单键输入和剪贴板功能
"""

import sys
import subprocess
from typing import Optional, Tuple

from .utils.terminal import TerminalOutput, Colors
from .utils.clipboard import Clipboard
from .utils.keyboard import SingleKeyInput


class InteractiveSelector:
    """交互式选择器"""
    
    OPTIONS = {
        'e': ('execute', 'Execute command'),
        'c': ('copy', 'Copy to clipboard'),
        'm': ('modify', 'Modify command'),
        's': ('skip', 'Skip/Cancel'),
        'h': ('help', 'Show help')
    }
    
    def __init__(self, enable_colors: bool = True):
        """
        初始化交互式选择器
        
        Args:
            enable_colors: 是否启用彩色输出
        """
        self.terminal = TerminalOutput(enable_colors=enable_colors)
    
    def show_command(self, command: str):
        """显示生成的命令"""
        self.terminal.print_box(
            title="Generated Command",
            content=f"  {command}",
            color=Colors.BRIGHT_CYAN
        )
    
    def show_options(self, single_key_mode: bool = True):
        """
        显示选项
        
        Args:
            single_key_mode: 是否使用单键模式
        """
        if single_key_mode:
            self.terminal.info("Please select an action:")
            options_text = "  "
            for key, (action, desc) in self.OPTIONS.items():
                options_text += f"[{key}] {desc}  "
            self.terminal.info(options_text)
            self.terminal.dim("Press key to select: ")
        else:
            print("\nPlease select an action:")
            for key, (action, desc) in self.OPTIONS.items():
                print(f"  [{key}] {desc}")
            print()
    
    def get_user_choice(self, single_key_mode: bool = True) -> Optional[str]:
        """
        获取用户选择
        
        Args:
            single_key_mode: 是否使用单键模式
            
        Returns:
            用户选择的操作，如果无效则返回 None
        """
        try:
            if single_key_mode:
                choice = SingleKeyInput.get_key()
                print()  # 换行
            else:
                choice = input("Please enter option: ").strip().lower()
            
            if choice in self.OPTIONS:
                return self.OPTIONS[choice][0]
            return None
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperation cancelled")
            return None
    
    def get_modified_command(self, original_command: str) -> Optional[str]:
        """
        获取用户修改后的命令
        
        Args:
            original_command: 原始命令
            
        Returns:
            修改后的命令，如果用户取消则返回 None
        """
        self.terminal.info(f"Current command: {original_command}")
        try:
            modified = input("Enter modified command (press Enter to use original): ").strip()
            if not modified:
                return original_command
            return modified
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperation cancelled")
            return None
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """
        执行命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            (是否成功, 输出内容)
        """
        self.terminal.info(f"Executing command: {command}")
        self.terminal.print_separator("-", 60)
        
        try:
            # 使用 shell=True 以支持管道等复杂命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 输出 stdout 和 stderr
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            success = result.returncode == 0
            output = (result.stdout + result.stderr).strip()
            
            self.terminal.print_separator("-", 60)
            if success:
                self.terminal.success("✓ Command executed successfully")
            else:
                self.terminal.error(f"✗ Command execution failed (exit code: {result.returncode})")
            
            return success, output
            
        except subprocess.TimeoutExpired:
            error_msg = "Command execution timeout (exceeded 5 minutes)"
            self.terminal.error(f"✗ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error executing command: {e}"
            self.terminal.error(f"✗ {error_msg}")
            return False, error_msg
    
    def copy_to_clipboard(self, command: str) -> bool:
        """
        复制命令到剪贴板
        
        Args:
            command: 要复制的命令
            
        Returns:
            是否成功
        """
        if Clipboard.copy(command):
            self.terminal.success("✓ Command copied to clipboard")
            return True
        else:
            self.terminal.error("✗ Failed to copy to clipboard (may need to install xclip/xsel/pyperclip)")
            return False
    
    def show_help(self):
        """显示帮助信息"""
        self.terminal.print_box(
            title="Help",
            content="""  [e] Execute command - Execute the generated command directly
  [c] Copy to clipboard - Copy command to clipboard
  [m] Modify command - Modify command before execution
  [s] Skip/Cancel - Do not execute command, return
  [h] Show help - Show this help information""",
            color=Colors.BRIGHT_BLUE
        )
