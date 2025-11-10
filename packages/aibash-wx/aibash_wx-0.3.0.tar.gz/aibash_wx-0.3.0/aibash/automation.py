"""
自动执行模式

提供在自动模式下，根据自然语言描述规划并执行多步命令的能力。
每一步命令或操作都会在执行前请求用户确认，执行结果会反馈给 AI 以便继续规划。
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import requests

from .interfaces.ai_agent import AIAgent
from .history import HistoryManager
from .interactive import InteractiveSelector
from .utils.terminal import TerminalOutput, Colors
from .config import AppConfig
from .i18n import t


AUTOMATION_PROMPT_TEMPLATE = """你是终端自动化助手，任务是根据用户提供的自然语言目标，规划并执行一系列终端操作。

必须严格遵守以下规则：
1. 你只能返回一段 JSON，不能包含任何额外文字或者解释。
2. JSON 须符合下面的结构（字段顺序不限）：
{{
  "action": "run_command" | "read_file" | "web_request" | "ask_user" | "finish",
  "reason": "<解释你的选择，简洁且不超过120个中文字>",
  "command": "<当 action 为 run_command 时的 shell 命令>",
  "path": "<当 action 为 read_file 时需要读取的绝对或相对路径>",
  "url": "<当 action 为 web_request 时需要访问的 URL>",
  "message": "<当 action 为 ask_user 或 finish 时要告诉用户的话>",
  "expectation": "<当 action 为 run_command、read_file 或 web_request 时，预期获得的结果提示>",
  "summary": "<仅在 action 为 finish 时提供对于整个任务的总结>"
}}
3. 所有非当前 action 需要的字段可以省略或设为 null。
4. 每次最多规划一个动作。
5. 如果需要更多信息，可以使用 "ask_user"。
6. 当你认为任务完成时，使用 "finish"，并提供 "message" 与 "summary"。

系统信息：
{system_info}

附加上下文摘要：
{environment_context}

当前工作目录：
{cwd}

用户任务：
{task}

历史记录（仅供参考）：
{history}

提示：
- 优先先勘察目录结构、依赖和关键文件，可以使用 shell 管道、Python 脚本或其他工具生成摘要后再继续任务。
- 当需要分析复杂文件或大输出时，分块处理或编写脚本辅助处理。
- 充分利用环境信息来定位项目结构、虚拟环境和 Git 状态。
- 尽量复用已有工具链；必要时可以临时编写小脚本（如 python - <<'PY' ... PY）完成分析。

请输出符合要求的 JSON。
"""


@dataclass
class AutomationStep:
    """记录自动化执行的步骤"""
    action: str
    status: str
    detail: str
    observation: str


class AutomationExecutor:
    """自动执行器"""
    
    MAX_STEPS = 20
    MAX_HISTORY_LINES = 12
    MAX_OBSERVATION_LENGTH = 1000
    MAX_REQUEST_TIMEOUT = 10
    JSON_PARSE_RETRIES = 2
    
    def __init__(
        self,
        agent: AIAgent,
        terminal: TerminalOutput,
        history_manager: HistoryManager,
        interactive: InteractiveSelector,
        config: AppConfig,
        use_new_terminal: bool = False,
        auto_options: Optional[Dict[str, Any]] = None,
        environment_context: str = ""
    ):
        self.agent = agent
        self.terminal = terminal
        self.history_manager = history_manager
        self.interactive = interactive
        self.config = config
        self.use_new_terminal = use_new_terminal
        self.auto_options = auto_options or {}
        self.auto_confirm_all = bool(self.auto_options.get('auto_confirm_all'))
        self.auto_confirm_commands = bool(self.auto_options.get('auto_confirm_commands'))
        self.auto_confirm_files = bool(self.auto_options.get('auto_confirm_files'))
        self.auto_confirm_web = bool(self.auto_options.get('auto_confirm_web'))
        self.max_steps = int(self.auto_options.get('max_steps') or self.MAX_STEPS)
        self.environment_context = environment_context
        self.steps: List[AutomationStep] = []
        self.silent_mode = bool(self.auto_options.get('allow_silence', True))
    
    def run(self, task: str):
        """执行自动化任务"""
        task = task.strip()
        if not task:
            self.terminal.error("✗ " + t("automation_task_empty"))
            return
        
        self.terminal.print_box(
            title=t("automation_title"),
            content=textwrap.dedent(f"""\
  {t("automation_task", task=task)}
  {t("automation_mode")}
  {t("automation_new_terminal", state=t("state_on") if self.use_new_terminal else t("state_off"))}"""),
            color=Colors.BRIGHT_MAGENTA
        )
        
        for step_idx in range(1, self.max_steps + 1):
            prompt = self._build_prompt(task)
            action_payload = self._request_action(prompt)
            if not action_payload:
                self.terminal.error("✗ " + t("automation_no_action"))
                break
            
            action = action_payload.get("action")
            reason = action_payload.get("reason", "")
            self.terminal.print_box(
                title=t("automation_step_plan", index=step_idx),
                content=textwrap.dedent(f"""\
  {t("automation_step_action", action=action)}
  {t("automation_step_reason", reason=reason or "-")}"""),
                color=Colors.BRIGHT_CYAN
            )
            
            continue_running = self._execute_action(action_payload)
            if not continue_running:
                break
        else:
            self.terminal.warning(t("automation_max_steps"))
    
    def _build_prompt(self, task: str) -> str:
        """构建发送给模型的 prompt"""
        system_info = self.config.system_info or "Unknown system"
        cwd = str(Path.cwd())
        history_text = self._format_history_for_prompt()
        
        return AUTOMATION_PROMPT_TEMPLATE.format(
            system_info=system_info,
            cwd=cwd,
            task=task,
            history=history_text,
            environment_context=self.environment_context or "（无额外上下文）"
        )
    
    def _format_history_for_prompt(self) -> str:
        """格式化历史步骤供模型参考"""
        if not self.steps:
            return "（暂无历史步骤）"
        
        lines: List[str] = []
        recent = self.steps[-self.MAX_HISTORY_LINES :]
        for idx, step in enumerate(recent, start=max(1, len(self.steps) - len(recent) + 1)):
            lines.append(f"[{idx}] action={step.action}, status={step.status}")
            lines.append(f"reason/detail={self._truncate(step.detail)}")
            lines.append(f"observation={self._truncate(step.observation)}")
        return "\n".join(lines)
    
    def _request_action(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用模型获取下一步动作"""
        for attempt in range(self.JSON_PARSE_RETRIES):
            response = self.agent.generate_command(prompt, expect_raw=True)
            payload = self._parse_json_response(response)
            if payload is not None:
                return payload
            prompt = self._augment_prompt_with_error(prompt, response)
        return None
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """解析模型返回的 JSON"""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试提取首尾括号之间的部分
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                snippet = text[start : end + 1]
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError:
                    return None
        return None
    
    def _augment_prompt_with_error(self, prompt: str, response: str) -> str:
        """在 prompt 中加入错误反馈，提醒模型输出有效 JSON"""
        feedback = textwrap.dedent(
            t("automation_prompt_invalid_json", response=response)
        )
        return prompt + "\n" + feedback
    
    def _execute_action(self, payload: Dict[str, Any]) -> bool:
        """执行具体动作并记录结果
        
        返回值：
            True 继续执行后续步骤
            False 停止自动模式
        """
        action = payload.get("action", "").lower()
        reason = payload.get("reason") or ""
        
        if action == "run_command":
            return self._handle_run_command(payload, reason)
        if action == "read_file":
            return self._handle_read_file(payload, reason)
        if action == "web_request":
            return self._handle_web_request(payload, reason)
        if action == "ask_user":
            return self._handle_ask_user(payload, reason)
        if action == "finish":
            return self._handle_finish(payload, reason)
        
        observation = t("automation_invalid_action", action=action)
        self._record_step(action or "unknown", "failed", reason, observation)
        self.terminal.error(f"✗ {observation}")
        return False
    
    def _handle_run_command(self, payload: Dict[str, Any], reason: str) -> bool:
        command = payload.get("command")
        expectation = payload.get("expectation", "")
        if not command:
            observation = t("automation_missing_command")
            self._record_step("run_command", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_missing_command"))
            return False
        
        self.terminal.info(t("automation_command_suggestion"))
        self.interactive.show_command(command)
        if expectation:
            self.terminal.dim(t("automation_command_expectation", expectation=expectation))
        
        if not self._confirm_with_user(t("automation_confirm_run_command"), action="run_command"):
            observation = t("automation_command_denied")
            self._record_step("run_command", "skipped", reason, observation)
            self.terminal.warning(t("automation_command_denied"))
            return True
        
        success, output = self.interactive.execute_command(
            command,
            use_new_terminal=self.use_new_terminal
        )
        observation = output or t("automation_no_output_captured")
        status = "success" if success else "failed"
        self._record_step("run_command", status, reason, observation)
        
        if self.history_manager.enabled:
            self.history_manager.add_record(
                command=command,
                output=output if self.config.history.include_output else "",
                success=success,
                user_query=""
            )
        if not success:
            self.terminal.warning(t("automation_command_failed"))
        return True
    
    def _handle_read_file(self, payload: Dict[str, Any], reason: str) -> bool:
        path_value = payload.get("path")
        if not path_value:
            observation = t("automation_missing_path")
            self._record_step("read_file", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_missing_path"))
            return False
        
        target_path = Path(path_value).expanduser().resolve()
        if not self.silent_mode:
            self.terminal.info(t("automation_file_request", path=target_path))
        
        if not self._confirm_with_user(t("automation_confirm_read_file"), action="read_file"):
            observation = t("automation_file_denied")
            self._record_step("read_file", "skipped", reason, observation)
            self.terminal.warning(t("automation_file_denied"))
            return True
        
        if not target_path.exists():
            observation = t("automation_file_missing", path=target_path)
            self._record_step("read_file", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_file_missing", path=target_path))
            return True
        
        try:
            preview, meta = self._generate_file_preview(target_path)
            self._record_step("read_file", "success", reason, f"{meta}\n{self._truncate(preview, 400)}")
            if not self.silent_mode:
                self.terminal.print_box(
                    title=t("automation_file_preview_title"),
                    content=f"{meta}\n\n{preview}",
                    color=Colors.BRIGHT_GREEN
                )
            return True
        except UnicodeDecodeError:
            observation = t("automation_file_binary")
            self._record_step("read_file", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_file_binary"))
            return True
        except Exception as e:
            observation = t("automation_file_error", error=e)
            self._record_step("read_file", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_file_error", error=e))
            return True
    
    def _handle_web_request(self, payload: Dict[str, Any], reason: str) -> bool:
        url = payload.get("url")
        expectation = payload.get("expectation", "")
        if not url:
            observation = t("automation_missing_url")
            self._record_step("web_request", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_missing_url"))
            return False
        
        if not self.silent_mode:
            self.terminal.info(t("automation_web_request", url=url))
            if expectation:
                self.terminal.dim(t("automation_web_expectation", expectation=expectation))
        
        if not url.lower().startswith(("http://", "https://")):
            observation = t("automation_web_protocol")
            self._record_step("web_request", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_web_protocol"))
            return True
        
        if not self._confirm_with_user(t("automation_confirm_web_request"), action="web_request"):
            observation = t("automation_web_denied")
            self._record_step("web_request", "skipped", reason, observation)
            self.terminal.warning(t("automation_web_denied"))
            return True
        
        try:
            return self._perform_web_request(url, reason, expectation, verify_ssl=True)
        except requests.exceptions.SSLError as ssl_error:
            self.terminal.error("✗ " + t("automation_ssl_error", error=ssl_error))
            if not self._confirm_with_user(t("automation_ssl_prompt", url=url), action="web_request"):
                observation = t("automation_ssl_denied")
                self._record_step("web_request", "skipped", reason, observation)
                self.terminal.warning(observation)
                return True
            try:
                return self._perform_web_request(url, reason, expectation, verify_ssl=False)
            except Exception as e:
                observation = t("automation_web_error", error=e)
                self._record_step("web_request", "failed", reason, observation)
                self.terminal.error("✗ " + t("automation_web_error", error=e))
                return True
        except Exception as e:
            observation = t("automation_web_error", error=e)
            self._record_step("web_request", "failed", reason, observation)
            self.terminal.error("✗ " + t("automation_web_error", error=e))
            return True
    
    def _handle_ask_user(self, payload: Dict[str, Any], reason: str) -> bool:
        message = payload.get("message") or "模型需要更多信息，请提供。"
        self.terminal.print_box(
            title=t("automation_question_title"),
            content=message,
            color=Colors.BRIGHT_YELLOW
        )
        user_input = input(t("automation_ask_user_prompt")).strip()
        observation = user_input or ""
        self._record_step("ask_user", "success", reason, observation)
        return True
    
    def _handle_finish(self, payload: Dict[str, Any], reason: str) -> bool:
        message = payload.get("message") or "模型认为任务已经完成。"
        summary = payload.get("summary") or ""
        
        self._record_step("finish", "success", reason, message + ("\n" + summary if summary else ""))
        self.terminal.print_box(
            title=t("automation_finish_title"),
            content=textwrap.dedent(f"""\
  {t("automation_finish_message", message=message)}
  {t("automation_finish_summary", summary=summary or "-")}"""),
            color=Colors.BRIGHT_GREEN
        )
        return False
    
    def _record_step(self, action: str, status: str, detail: str, observation: str):
        """记录步骤信息"""
        self.steps.append(
            AutomationStep(
                action=action,
                status=status,
                detail=detail or "",
                observation=self._truncate(observation)
            )
        )
    
    def _truncate(self, text: str, limit: int = 400) -> str:
        """截断文本"""
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."
    
    def _confirm_with_user(self, prompt: str, action: str) -> bool:
        """请求用户确认"""
        if self.auto_confirm_all:
            return True
        if action == "run_command" and self.auto_confirm_commands:
            return True
        if action == "read_file" and self.auto_confirm_files:
            return True
        if action == "web_request" and self.auto_confirm_web:
            return True
        try:
            choice = input(prompt).strip().lower()
            return choice in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            self.terminal.warning(t("common_operation_cancelled"))
            return False

    def _perform_web_request(self, url: str, reason: str, expectation: str, verify_ssl: bool = True) -> bool:
        """执行具体的网络请求逻辑"""
        response = requests.get(url, timeout=self.MAX_REQUEST_TIMEOUT, verify=verify_ssl)
        content_type = response.headers.get("Content-Type", "")
        text = response.text
        preview = self._truncate(text, self.MAX_OBSERVATION_LENGTH)
        status_line = f"HTTP {response.status_code} {response.reason}"
        note = ""
        if not verify_ssl:
            note = "\n" + t("automation_ssl_unverified_note")
        observation = f"{status_line}; Content-Type={content_type}; Preview:\n{preview}{note}"
        self._record_step("web_request", "success", reason, observation)
        if not self.silent_mode:
            self.terminal.print_box(
                title="Web Response Preview",
                content=preview,
                color=Colors.BRIGHT_GREEN
            )
            if note:
                self.terminal.warning(t("automation_ssl_unverified_note"))
        return True

    def _generate_file_preview(self, path: Path) -> tuple[str, str]:
        """生成文件预览（支持大文件分段读取）"""
        max_preview_bytes = 4000
        size_bytes = path.stat().st_size
        encoding = "utf-8"
        head_text = ""
        tail_text = ""
        truncated = False

        with path.open('rb') as f:
            data = f.read(max_preview_bytes)
            head_text = data.decode(encoding, errors='replace')
            if size_bytes > max_preview_bytes * 2:
                truncated = True
                f.seek(-max_preview_bytes, 2)
                tail = f.read(max_preview_bytes)
                tail_text = tail.decode(encoding, errors='replace')
            elif size_bytes > max_preview_bytes:
                truncated = True
                tail_text = ""

        preview_parts = [head_text.rstrip()]
        if tail_text:
            preview_parts.append("\n... [middle omitted] ...\n")
            preview_parts.append(tail_text.lstrip())
        preview = "".join(preview_parts)

        head_lines = head_text.count("\n")
        tail_lines = tail_text.count("\n") if tail_text else 0
        if not truncated:
            approx_lines = head_lines + (1 if head_text and not head_text.endswith("\n") else 0)
        else:
            approx_lines = f">= {head_lines + tail_lines}"

        meta = f"Path: {path}\nSize: {size_bytes} bytes\nLines (approx): {approx_lines}"
        if truncated:
            meta += "\nPreview: head and tail segments shown (content truncated)"
        else:
            meta += "\nPreview: full content"
        return preview, meta

    def enable_silent_outputs(self, silent: bool = True):
        self.silent_mode = silent

