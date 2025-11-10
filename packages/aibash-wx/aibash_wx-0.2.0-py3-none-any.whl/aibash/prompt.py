"""
Prompt 管理模块

提供默认 prompt 和用户自定义 prompt 支持
"""

from typing import List, Dict, Any
from importlib.resources import files


class PromptManager:
    """Prompt 管理器"""
    
    @staticmethod
    def get_default_prompt() -> str:
        """获取默认 prompt"""
        try:
            # 尝试从资源文件加载
            prompt_file = files("aibash.resources").joinpath("__init__.py")
            # 如果资源文件不存在，使用硬编码的默认值
            return PromptManager.DEFAULT_PROMPT
        except Exception:
            return PromptManager.DEFAULT_PROMPT
    
    DEFAULT_PROMPT = """你是一个专业的命令行助手，能够根据用户的自然语言描述生成对应的shell命令。

要求：
1. 只输出shell命令，不要包含任何解释、说明或其他文本
2. 命令应该是单行的，可以直接在终端执行
3. 确保命令的安全性，避免危险的命令（如删除重要文件、格式化磁盘等）
4. 如果用户的需求不明确，生成最常用和安全的命令
5. 优先使用跨平台兼容的命令（如使用python而不是bash特定语法）

系统信息：
{system_info}

{history_context}

用户需求：{user_query}

请直接输出shell命令，不要包含任何其他内容："""
    
    FAILURE_RECOVERY_PROMPT_ZH = """你是一名命令行专家，正在帮助用户修复失败的命令。

当前系统信息：
{system_info}

原始需求：
{user_query}

失败的命令：
{failed_command}

错误输出（如有截断请依然充分参考）：
{error_output}

历史上下文（最近执行情况）：
{history_context}

请分析失败原因，生成一个新的、可直接执行且更可靠的命令，并附上一句简洁的中文提示建议，输出格式为：
命令: <新命令>
提示: <一句话提示>
"""
    
    FAILURE_RECOVERY_PROMPT_EN = """You are a command-line expert helping the user fix a failed command.

System information:
{system_info}

Original request:
{user_query}

Failed command:
{failed_command}

Error output (use the portion provided even if truncated):
{error_output}

Recent execution history (if any):
{history_context}

Please analyse the failure, generate a safer replacement command, and output in the format:
Command: <new command>
Tip: <one-sentence hint>
"""
    
    @staticmethod
    def format_prompt(
        user_query: str,
        system_info: str = "",
        history_context: str = "",
        custom_prompt: str = ""
    ) -> str:
        """
        格式化 prompt
        
        Args:
            user_query: 用户查询
            system_info: 系统信息
            history_context: 历史上下文
            custom_prompt: 自定义 prompt
            
        Returns:
            格式化后的 prompt
        """
        if custom_prompt:
            template = custom_prompt
        else:
            template = PromptManager.DEFAULT_PROMPT
        
        return template.format(
            system_info=system_info or "未知系统",
            history_context=history_context or "",
            user_query=user_query
        )
    
    @staticmethod
    def format_failure_prompt(
        user_query: str,
        failed_command: str,
        error_output: str,
        system_info: str = "",
        history_context: str = ""
    ) -> str:
        """格式化命令失败后用于恢复的 prompt"""
        from .i18n import I18n
        language = I18n.get_language()
        template = (
            PromptManager.FAILURE_RECOVERY_PROMPT_ZH
            if language == "zh"
            else PromptManager.FAILURE_RECOVERY_PROMPT_EN
        )
        default_system = "未知系统" if language == "zh" else "Unknown system"
        default_error_output = "（无错误输出）" if language == "zh" else "(no error output)"
        default_history = "（无历史记录）" if language == "zh" else "(no history yet)"
        return template.format(
            system_info=system_info or default_system,
            user_query=user_query,
            failed_command=failed_command,
            error_output=error_output or default_error_output,
            history_context=history_context or default_history
        )
    
    @staticmethod
    def format_history_context(history_records: List[Dict[str, Any]]) -> str:
        """
        格式化历史记录为上下文
        
        Args:
            history_records: 历史记录列表
            
        Returns:
            格式化的历史上下文字符串
        """
        if not history_records:
            return ""
        
        context_lines = ["\n最近的命令执行历史："]
        for i, record in enumerate(history_records[-10:], 1):  # 只取最近10条
            cmd = record.get('command', '')
            output = record.get('output', '')
            success = record.get('success', True)
            
            context_lines.append(f"\n{i}. 命令: {cmd}")
            if output:
                # 截断过长的输出
                output_preview = output[:200] + "..." if len(output) > 200 else output
                context_lines.append(f"   输出: {output_preview}")
            context_lines.append(f"   状态: {'成功' if success else '失败'}")
        
        return "\n".join(context_lines)

