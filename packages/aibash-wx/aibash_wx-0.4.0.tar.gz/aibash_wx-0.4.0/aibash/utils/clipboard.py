"""
剪贴板工具 - 跨平台剪贴板支持
"""

import platform
import subprocess


class Clipboard:
    """剪贴板工具"""
    
    @staticmethod
    def copy(text: str) -> bool:
        """
        复制文本到剪贴板
        
        Args:
            text: 要复制的文本
            
        Returns:
            是否成功
        """
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=text.encode('utf-8'))
                return process.returncode == 0
            
            elif system == "Windows":
                # Windows 使用 clip.exe
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=text.encode('utf-8'))
                return process.returncode == 0
            
            else:  # Linux 和其他 Unix 系统
                # 尝试使用 xclip 或 xsel
                for cmd in ['xclip', 'xsel']:
                    try:
                        if cmd == 'xclip':
                            process = subprocess.Popen(
                                ['xclip', '-selection', 'clipboard'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            )
                        else:  # xsel
                            process = subprocess.Popen(
                                ['xsel', '--clipboard', '--input'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            )
                        process.communicate(input=text.encode('utf-8'))
                        if process.returncode == 0:
                            return True
                    except FileNotFoundError:
                        continue
                
                # 如果都不可用，尝试使用 pyperclip
                try:
                    import pyperclip
                    pyperclip.copy(text)
                    return True
                except ImportError:
                    return False
        
        except Exception:
            return False
    
    @staticmethod
    def paste() -> str:
        """
        从剪贴板获取文本
        
        Returns:
            剪贴板内容
        """
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                result = subprocess.run(
                    ['pbpaste'],
                    capture_output=True,
                    text=True
                )
                return result.stdout
            
            elif system == "Windows":
                # Windows 需要特殊处理，使用 pyperclip 更可靠
                try:
                    import pyperclip
                    return pyperclip.paste()
                except ImportError:
                    return ""
            
            else:  # Linux
                for cmd in ['xclip', 'xsel']:
                    try:
                        if cmd == 'xclip':
                            result = subprocess.run(
                                ['xclip', '-selection', 'clipboard', '-o'],
                                capture_output=True,
                                text=True
                            )
                        else:  # xsel
                            result = subprocess.run(
                                ['xsel', '--clipboard', '--output'],
                                capture_output=True,
                                text=True
                            )
                        if result.returncode == 0:
                            return result.stdout
                    except FileNotFoundError:
                        continue
                
                # 回退到 pyperclip
                try:
                    import pyperclip
                    return pyperclip.paste()
                except ImportError:
                    return ""
        
        except Exception:
            return ""

