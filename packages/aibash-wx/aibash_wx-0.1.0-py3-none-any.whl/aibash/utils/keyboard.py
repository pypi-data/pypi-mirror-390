"""
单键输入工具 - 跨平台单键输入支持
"""

import sys


class SingleKeyInput:
    """单键输入工具"""
    
    @staticmethod
    def get_key() -> str:
        """
        获取单个按键输入
        
        Returns:
            按键字符（小写）
        """
        if sys.platform == "win32":
            import msvcrt
            try:
                key = msvcrt.getch().decode("utf-8")
                return key.lower()
            except Exception:
                return input().strip().lower()
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                key = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return key.lower()

