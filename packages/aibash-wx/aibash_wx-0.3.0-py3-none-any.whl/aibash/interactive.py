"""
交互式命令选择模块

提供用户交互界面，让用户选择执行/修改/放弃命令
支持单键输入和剪贴板功能
"""

import sys
import subprocess
import platform
import shutil
from typing import Optional, Tuple

from .utils.terminal import TerminalOutput, Colors
from .utils.clipboard import Clipboard
from .utils.keyboard import SingleKeyInput
from .i18n import t


class InteractiveSelector:
    """交互式选择器"""
    
    MAX_OUTPUT_CHARS = 8000
    OUTPUT_HEAD_CHARS = 4000
    OUTPUT_TAIL_CHARS = 2000
    
    OPTIONS = {
        'e': ('execute', 'interactive_option_execute'),
        'c': ('copy', 'interactive_option_copy'),
        'm': ('modify', 'interactive_option_modify'),
        's': ('skip', 'interactive_option_skip'),
        'h': ('help', 'interactive_option_help')
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
            title=t("common_generated_command_title"),
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
            self.terminal.info(t("interactive_prompt_select"))
            options_text = "  "
            for key, (_, desc_key) in self.OPTIONS.items():
                options_text += f"{t(desc_key)}  "
            self.terminal.info(options_text.strip())
            self.terminal.dim(t("common_press_key"))
        else:
            print(f"\n{t('interactive_prompt_select')}")
            for key, (_, desc_key) in self.OPTIONS.items():
                print(f"  {t(desc_key)}")
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
                choice = input(t("common_enter_option")).strip().lower()
            
            if choice in self.OPTIONS:
                return self.OPTIONS[choice][0]
            return None
        except (EOFError, KeyboardInterrupt):
            print("\n\n" + t("common_operation_cancelled"))
            return None
    
    def get_modified_command(self, original_command: str) -> Optional[str]:
        """
        获取用户修改后的命令
        
        Args:
            original_command: 原始命令
            
        Returns:
            修改后的命令，如果用户取消则返回 None
        """
        self.terminal.info(t("interactive_current_command", command=original_command))
        try:
            modified = input(t("interactive_enter_modified")).strip()
            if not modified:
                return original_command
            return modified
        except (EOFError, KeyboardInterrupt):
            print("\n\n" + t("common_operation_cancelled"))
            return None
    
    def execute_command(self, command: str, use_new_terminal: bool = False) -> Tuple[bool, str]:
        """
        执行命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            (是否成功, 输出内容)
        """
        if use_new_terminal:
            result = self._execute_in_new_terminal(command)
            if result is not None:
                return result
            self.terminal.warning(t("automation_new_terminal_failed"))
        
        return self._execute_in_current_terminal(command)
    
    def _execute_in_current_terminal(self, command: str) -> Tuple[bool, str]:
        """在当前终端执行命令"""
        self.terminal.info(t("interactive_executing", command=command))
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
                self._print_stream(result.stdout, is_stderr=False)
            if result.stderr:
                self._print_stream(result.stderr, is_stderr=True)
            
            success = result.returncode == 0
            output = (result.stdout + result.stderr).strip()
            
            self.terminal.print_separator("-", 60)
            if success:
                self.terminal.success(t("interactive_execution_success"))
            else:
                self.terminal.error(t("interactive_execution_failed", code=result.returncode))
            
            return success, output
            
        except subprocess.TimeoutExpired:
            error_msg = t("interactive_execution_timeout")
            self.terminal.error(f"✗ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = t("interactive_execution_error", error=e)
            self.terminal.error(f"✗ {error_msg}")
            return False, error_msg
    
    def _execute_in_new_terminal(self, command: str) -> Optional[Tuple[bool, str]]:
        """
        在新终端中执行命令
        
        Returns:
            (是否成功, 输出描述) 或 None（表示无法在新终端执行，需要回退）
        """
        system = platform.system()
        self.terminal.info(t("interactive_launch_new_terminal", command=command))
        
        try:
            if system == "Linux":
                return self._launch_linux_terminal(command)
            if system == "Darwin":
                return self._launch_macos_terminal(command)
            if system == "Windows":
                return self._launch_windows_terminal(command)
            self.terminal.warning(f"Unsupported platform for new terminal execution: {system}")
            return None
        except Exception as e:
            error_msg = t("automation_new_terminal_error", error=e)
            self.terminal.error(f"✗ {error_msg}")
            return False, error_msg

    def _wrap_command_for_bash(self, command: str) -> str:
        """包装命令，确保终端窗口执行后保持打开状态"""
        sanitized = command.replace('"', '\\"')
        return f"{sanitized}; echo; exec bash"

    def _launch_linux_terminal(self, command: str) -> Optional[Tuple[bool, str]]:
        """在 Linux 上尝试使用常见终端模拟器执行命令"""
        wrapped = self._wrap_command_for_bash(command)
        candidates = [
            ("gnome-terminal", ["gnome-terminal", "--", "bash", "-lc", wrapped]),
            ("konsole", ["konsole", "--noclose", "-e", "bash", "-lc", wrapped]),
            ("xterm", ["xterm", "-hold", "-e", "bash", "-lc", wrapped]),
        ]
        
        for term, args in candidates:
            if shutil.which(term):
                subprocess.Popen(args)
                self.terminal.success(t("interactive_command_launched", terminal=term))
                message = f"{t('interactive_command_launched', terminal=term)}; {t('interactive_output_not_captured')}"
                return True, message
        
        self.terminal.warning(t("interactive_no_terminal_found"))
        return None
    
    def _launch_macos_terminal(self, command: str) -> Tuple[bool, str]:
        """在 macOS 上打开终端执行命令"""
        escaped = command.replace('"', '\\"')
        osa_command = f'tell application "Terminal" to do script "{escaped}"'
        subprocess.Popen(["osascript", "-e", osa_command])
        self.terminal.success(t("interactive_mac_terminal"))
        return True, f"{t('interactive_mac_terminal')}; {t('interactive_output_not_captured')}"
    
    def _launch_windows_terminal(self, command: str) -> Tuple[bool, str]:
        """在 Windows 上打开新的命令提示符窗口执行命令"""
        escaped = command.replace('"', '\\"')
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "cmd.exe", "/k", escaped],
            creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, "CREATE_NEW_CONSOLE") else 0
        )
        self.terminal.success(t("interactive_windows_terminal"))
        return True, f"{t('interactive_windows_terminal')}; {t('interactive_output_not_captured')}"
    
    def copy_to_clipboard(self, command: str) -> bool:
        """
        复制命令到剪贴板
        
        Args:
            command: 要复制的命令
            
        Returns:
            是否成功
        """
        if Clipboard.copy(command):
            self.terminal.success(t("interactive_copy_success"))
            return True
        else:
            self.terminal.error(t("interactive_copy_failed"))
            return False
    
    def show_help(self):
        """显示帮助信息"""
        content = "\n".join([
            f"  {t('interactive_option_execute')}",
            f"  {t('interactive_option_copy')}",
            f"  {t('interactive_option_modify')}",
            f"  {t('interactive_option_skip')}",
            f"  {t('interactive_option_help')}",
        ])
        self.terminal.print_box(
            title=t("common_help_title"),
            content=content,
            color=Colors.BRIGHT_BLUE
        )

    def _print_stream(self, text: str, is_stderr: bool = False):
        """限制大输出，避免刷屏"""
        if len(text) <= self.MAX_OUTPUT_CHARS:
            print(text, file=sys.stderr if is_stderr else sys.stdout, end="")
            if text and not text.endswith("\n"):
                print(file=sys.stderr if is_stderr else sys.stdout)
            return
        head = text[:self.OUTPUT_HEAD_CHARS]
        tail = text[-self.OUTPUT_TAIL_CHARS:]
        stream = sys.stderr if is_stderr else sys.stdout
        print(head, file=stream, end="")
        if not head.endswith("\n"):
            print(file=stream)
        print("... [output truncated] ...", file=stream)
        print(tail, file=stream, end="" if tail.endswith("\n") else "\n", flush=True)
