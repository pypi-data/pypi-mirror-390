"""
终端输出工具 - 彩色输出和格式化
"""

import sys
import platform


class Colors:
    """ANSI 颜色代码"""
    # 基本颜色
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 亮色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class TerminalOutput:
    """终端输出工具"""
    
    def __init__(self, enable_colors: bool = True):
        """
        初始化终端输出工具
        
        Args:
            enable_colors: 是否启用颜色（Windows 可能需要特殊处理）
        """
        self.enable_colors = enable_colors and self._supports_colors()
    
    def _supports_colors(self) -> bool:
        """检查终端是否支持颜色"""
        # Windows 10+ 支持 ANSI，但需要检查
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 启用虚拟终端处理
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return False
        return True
    
    def colorize(self, text: str, color: str) -> str:
        """为文本添加颜色"""
        if not self.enable_colors:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def success(self, text: str):
        """成功消息（绿色）"""
        print(self.colorize(text, Colors.BRIGHT_GREEN))
    
    def error(self, text: str):
        """错误消息（红色）"""
        print(self.colorize(text, Colors.BRIGHT_RED), file=sys.stderr)
    
    def info(self, text: str):
        """信息消息（蓝色）"""
        print(self.colorize(text, Colors.BRIGHT_BLUE))
    
    def warning(self, text: str):
        """警告消息（黄色）"""
        print(self.colorize(text, Colors.BRIGHT_YELLOW))
    
    def command(self, text: str):
        """命令显示（青色）"""
        print(self.colorize(text, Colors.BRIGHT_CYAN))
    
    def dim(self, text: str):
        """暗淡文本"""
        print(self.colorize(text, Colors.DIM))
    
    def print_separator(self, char: str = "=", length: int = 60):
        """打印分隔线"""
        print(self.colorize(char * length, Colors.DIM))
    
    def print_box(self, title: str, content: str, color: str = Colors.BRIGHT_BLUE):
        """打印带边框的文本"""
        if not self.enable_colors:
            print(f"\n{title}")
            print("=" * len(title))
            print(content)
            print("=" * len(title))
        else:
            border = "=" * max(len(title), len(content.split('\n')[0]) if content else 0)
            print(f"\n{self.colorize(border, color)}")
            print(self.colorize(title, color))
            print(self.colorize(border, color))
            print(content)
            print(self.colorize(border, color))

