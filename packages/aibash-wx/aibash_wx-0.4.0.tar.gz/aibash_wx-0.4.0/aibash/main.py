"""
AIBash 主程序入口

处理命令行参数和核心逻辑
"""

import sys
import argparse
import math
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Optional, List

from .config import ConfigManager
from .agents.agent_builder import AgentBuilder
from .history import HistoryManager
from .interactive import InteractiveSelector
from .prompt import PromptManager
from .utils.terminal import TerminalOutput, Colors
from . import config_init
from .automation import AutomationExecutor
from .i18n import I18n, t
from .context import ContextCollector
from .summary_cache import ProjectSummaryCache


class AIBash:
    """AIBash 主类"""
    
    SUMMARY_ALLOWED_SUFFIXES = {
        ".py", ".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".toml", ".ini",
        ".cfg", ".conf", ".sh", ".bash", ".zsh", ".js", ".ts", ".tsx", ".jsx",
        ".java", ".kt", ".swift", ".go", ".rs", ".c", ".cc", ".cpp", ".h", ".hpp",
        ".cs", ".php", ".rb", ".scala"
    }
    SUMMARY_MAX_FILES = 200
    SUMMARY_CONTEXT_FILES = 12
    SUMMARY_CHUNK_SIZE = 4000
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 AIBash
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.language = self.config.ui.get('language', 'en')
        I18n.set_language(self.language)
        
        # 初始化终端输出与历史记录管理器
        self.terminal = TerminalOutput(enable_colors=self.config.ui.get('enable_colors', True))
        self.history_manager = HistoryManager(
            history_file=self.config.history.history_file,
            max_records=self.config.history.max_records,
            enabled=self.config.history.enabled
        )
        
        # 环境上下文及摘要
        self.summary_workers = max(1, self.config.automation.summary_workers)
        self.environment_context = self._build_environment_context()
        
        # 初始化交互式选择器
        self.interactive = InteractiveSelector(
            enable_colors=self.config.ui.get('enable_colors', True)
        )
        
        # 初始化 AI Agent
        self.agent = None
        self._init_agent()
    
    def set_language(self, language: Optional[str]):
        """切换界面语言"""
        if not language:
            return
        I18n.set_language(language)
        self.language = I18n.get_language()
        self.config.ui['language'] = self.language
        try:
            self.config_manager.save_config()
        except Exception as e:
            self.terminal.warning(t("warn_language_persist_failed", error=e))
    
    def _gather_summary_files(self, path: Path, limit: int | None = None) -> List[Path]:
        files: List[Path] = []
        if path.is_file():
            if self._is_text_file(path):
                files.append(path)
            return files
        max_files = limit or self.SUMMARY_MAX_FILES
        for file_path in path.rglob("*"):
            if len(files) >= max_files:
                break
            if not file_path.is_file():
                continue
            if "__pycache__" in file_path.parts:
                continue
            if not self._is_text_file(file_path):
                continue
            files.append(file_path)
        return files
    
    def _is_text_file(self, path: Path) -> bool:
        suffix = path.suffix.lower()
        if suffix and suffix not in self.SUMMARY_ALLOWED_SUFFIXES:
            # 允许未知后缀但需进一步检测
            pass
        try:
            with path.open('rb') as f:
                sample = f.read(1024)
                if b'\0' in sample:
                    return False
        except Exception:
            return False
        return True
    
    def _summarize_file(self, file_path: Path, agent) -> Optional[str]:
        try:
            text = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                text = file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                self.terminal.warning(t("error_summarize_not_text", path=file_path))
                return None
        except Exception:
            self.terminal.warning(t("error_summarize_not_text", path=file_path))
            return None
        
        text = text.strip()
        if not text:
            return "（文件为空）"
        
        if len(text) <= self.SUMMARY_CHUNK_SIZE:
            prompt = PromptManager.format_summary_prompt(file_path, text, 1, 1)
            try:
                summary = agent.generate_command(prompt, expect_raw=True)
            except Exception as exc:
                self.terminal.error(t("error_generate_command", error=exc))
                return None
            return summary.strip()
        
        chunk_summaries: List[str] = []
        total_chunks = math.ceil(len(text) / self.SUMMARY_CHUNK_SIZE)
        for idx in range(total_chunks):
            start = idx * self.SUMMARY_CHUNK_SIZE
            chunk = text[start:start + self.SUMMARY_CHUNK_SIZE]
            prompt = PromptManager.format_summary_prompt(file_path, chunk, idx + 1, total_chunks)
            try:
                chunk_summary = agent.generate_command(prompt, expect_raw=True).strip()
            except Exception as exc:
                self.terminal.error(t("error_generate_command", error=exc))
                return None
            chunk_summaries.append(chunk_summary)
        
        aggregate_prompt = PromptManager.format_summary_aggregation(file_path, chunk_summaries)
        try:
            final_summary = agent.generate_command(aggregate_prompt, expect_raw=True)
        except Exception as exc:
            self.terminal.error(t("error_generate_command", error=exc))
            return None
        return final_summary.strip()
    
    def _init_agent(self):
        """初始化 AI Agent"""
        model_config = self.config.model
        if not model_config.api_key and model_config.provider == "openai":
            self.terminal.warning(t("warn_api_key_missing"))
            return
        
        try:
            self.agent = self._build_agent_instance()
        except Exception as e:
            self.terminal.error(t("error_agent_init_failed", error=e))
    
    def _build_agent_instance(self):
        return AgentBuilder.build_agent(
            self.config.model,
            temperature=self.config.model_params.get('temperature', 0.3),
            max_tokens=self.config.model_params.get('max_tokens', 500),
            timeout=self.config.model_params.get('timeout', 30)
        )

    def _build_environment_context(self) -> str:
        try:
            base = ContextCollector(Path.cwd()).collect()
        except Exception:
            base = ""
        return base

    def _generate_project_summary(self, root: Path, workers: int) -> str:
        files = self._gather_summary_files(root, limit=self.SUMMARY_CONTEXT_FILES)
        if not files:
            return ""
        
        cache = ProjectSummaryCache(root)
        cache.load()
        thread_local = threading.local()
        summaries: List[tuple[Path, str]] = []
        to_process: List[tuple[Path, float]] = []
        
        for file_path in files:
            mtime = file_path.stat().st_mtime
            cached_summary = cache.get_summary(file_path, mtime)
            if cached_summary:
                relative = file_path.relative_to(root) if file_path.is_absolute() else file_path
                self.terminal.dim(t("info_summary_cache_used", path=relative))
                summaries.append((relative, cached_summary))
            else:
                to_process.append((file_path, mtime))
        
        if to_process:
            workers = min(workers, len(to_process))
            self.terminal.dim(t("info_summarize_start", path=root, count=len(to_process)))

            def worker(item):
                file_path, mtime = item
                if not hasattr(thread_local, "agent"):
                    try:
                        thread_local.agent = self._build_agent_instance()
                    except Exception as exc:
                        return file_path, mtime, None, exc
                agent = thread_local.agent
                summary = self._summarize_file(file_path, agent)
                return file_path, mtime, summary, None

            with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
                futures = [executor.submit(worker, item) for item in to_process]
                for future in as_completed(futures):
                    file_path, mtime, summary, error = future.result()
                    if error:
                        self.terminal.error(t("error_generate_command", error=error))
                        continue
                    if not summary:
                        continue
                    cache.update_summary(file_path, mtime, summary)
                    relative = file_path.relative_to(root) if file_path.is_absolute() else file_path
                    summaries.append((relative, summary))
            cache.save()
            self.terminal.dim(t("info_summary_cache_saved", count=len(to_process)))
        
        self.terminal.dim(t("info_summarize_done"))
        
        summaries.sort(key=lambda item: str(item[0]))
        return "\n".join(f"- {path}: {self._truncate_summary(summary)}" for path, summary in summaries)

    @staticmethod
    def _truncate_summary(summary: str, limit: int = 220) -> str:
        summary = " ".join(summary.split())
        if len(summary) <= limit:
            return summary
        return summary[:limit] + "..."
    
    def run_project_analysis(
        self,
        user_query: str,
        use_new_terminal: bool = False,
        auto_options: Optional[dict] = None
    ):
        """项目分析模式：生成项目摘要后执行自动模式"""
        if not self.agent:
            self.terminal.error(t("error_agent_not_initialized"))
            return
        
        options = auto_options or {}
        options.setdefault('summary_workers', self.summary_workers)
        base_env = self.environment_context or self._build_environment_context()
        summary_text = self._generate_project_summary(Path.cwd(), options.get('summary_workers', self.summary_workers))
        environment_context = base_env
        if summary_text:
            environment_context = (environment_context + f"\n\n【Project Summary】\n{summary_text}").strip()
        
        options['enable_auto_summary'] = False
        self.process_auto_task(
            user_query=user_query,
            use_new_terminal=use_new_terminal,
            auto_options=options,
            environment_override=environment_context
        )
    
    def generate_command(self, user_query: str) -> Optional[str]:
        """
        生成命令
        
        Args:
            user_query: 用户查询
            
        Returns:
            生成的命令，如果失败则返回 None
        """
        if not self.agent:
            self.terminal.error(t("error_agent_not_initialized"))
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
            custom_prompt=self.config.custom_prompt if not self.config.use_default_prompt else "",
            environment_context=self.environment_context
        )
        
        try:
            self.terminal.info(t("info_generating_command"))
            command = self.agent.generate_command(prompt)
            return command
        except Exception as e:
            self.terminal.error(t("error_generate_command", error=e))
            return None
    
    def process_query(self, user_query: str, use_new_terminal: bool = False):
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
                self.terminal.warning(t("common_invalid_option"))
                continue
            
            if choice == 'help':
                self.interactive.show_help()
                continue
            
            if choice == 'skip':
                self.terminal.info(t("info_command_cancelled"))
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
                success, output = self.interactive.execute_command(
                    command,
                    use_new_terminal=use_new_terminal
                )
                
                # 保存历史记录
                if self.config.history.enabled:
                    self.history_manager.add_record(
                        command=command,
                        output=output if self.config.history.include_output else "",
                        success=success,
                        user_query=user_query
                    )
                
                if success:
                    return
                
                # 命令执行失败，尝试自动恢复
                recovery = self._attempt_command_recovery(
                    user_query=user_query,
                    failed_command=command,
                    error_output=output
                )
                
                if recovery and recovery['command'] and recovery['command'] != command:
                    command = recovery['command']
                    tip = recovery.get('tip', '')
                    content = t("label_command", command=command)
                    if tip:
                        content += f"\n{t('label_tip', tip=tip)}"
                    self.terminal.print_box(
                        title=t("title_recovery_suggestion"),
                        content=content,
                        color=Colors.BRIGHT_YELLOW
                    )
                    continue
                
                # 如果无法恢复或命令未变化，则结束
                return

    def process_auto_task(
        self,
        user_query: str,
        use_new_terminal: bool = False,
        auto_options: Optional[dict] = None,
        environment_override: Optional[str] = None
    ):
        """
        处理自动化任务
        
        Args:
            user_query: 用户查询/任务描述
            use_new_terminal: 是否在新终端中执行命令
        """
        if not self.agent:
            self.terminal.error(t("error_agent_not_initialized"))
            return
        
        config_auto = asdict(self.config.automation)
        merged_options = dict(config_auto)
        auto_options = auto_options or {}
        for key, value in auto_options.items():
            if value is not None:
                merged_options[key] = value

        if environment_override is not None:
            environment_context = environment_override
            merged_options['enable_auto_summary'] = False
        else:
            environment_context = self.environment_context or self._build_environment_context()
            if merged_options.get('enable_auto_summary', False):
                summary_workers = max(1, merged_options.get('summary_workers', self.summary_workers))
                project_summary = self._generate_project_summary(Path.cwd(), summary_workers)
                if project_summary:
                    environment_context = (environment_context + f"\n\n【Project Summary】\n{project_summary}").strip()
        
        executor = AutomationExecutor(
            agent=self.agent,
            terminal=self.terminal,
            history_manager=self.history_manager,
            interactive=self.interactive,
            config=self.config,
            use_new_terminal=use_new_terminal,
            auto_options=merged_options,
            environment_context=environment_context
        )

        executor.enable_silent_outputs(merged_options.get('allow_silence', True))

        executor.run(user_query)

    def _attempt_command_recovery(self, user_query: str, failed_command: str, error_output: str) -> Optional[dict]:
        """
        在命令执行失败后尝试生成新的命令建议
        
        Returns:
            dict 包含 'command' 和可选 'tip' 字段，若失败返回 None
        """
        if not self.agent:
            return None
        
        history_context = ""
        if self.config.history.enabled and self.config.history.include_output:
            recent_records = self.history_manager.get_recent_records(10)
            history_context = PromptManager.format_history_context(recent_records)
        
        prompt = PromptManager.format_failure_prompt(
            user_query=user_query,
            failed_command=failed_command,
            error_output=error_output or "",
            system_info=self.config.system_info,
            history_context=history_context
        )
        
        try:
            self.terminal.warning(t("warn_generating_recovery"))
            response = self.agent.generate_command(prompt, expect_raw=True)
            command, tip = self._parse_recovery_response(response)
            if not command:
                return None
            return {'command': command, 'tip': tip}
        except Exception as e:
            self.terminal.error(t("error_recovery_failed", error=e))
            return None

    @staticmethod
    def _parse_recovery_response(response: str) -> tuple:
        """解析恢复命令响应"""
        if not response:
            return "", ""
        
        command = ""
        tip = ""
        for line in response.splitlines():
            stripped = line.strip()
            if stripped.startswith("命令:"):
                command = stripped.split("命令:", 1)[1].strip()
            elif stripped.lower().startswith("command:"):
                command = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("提示:"):
                tip = stripped.split("提示:", 1)[1].strip()
            elif stripped.lower().startswith("tip:"):
                tip = stripped.split(":", 1)[1].strip()
        
        # 如果没有解析到命令，尝试将整段作为命令
        if not command:
            command = response.strip().splitlines()[0].strip()
        return command, tip


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='aibash',
        description=t("parser_description"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=t("parser_epilog"),
        usage=t("parser_usage", prog='aibash')
    )
    
    query_group = parser.add_mutually_exclusive_group()
    
    query_group.add_argument(
        '-l', '--lang',
        dest='query',
        metavar='QUERY',
        help=t("help_lang_option")
    )
    
    query_group.add_argument(
        '-a', '--auto',
        dest='auto_query',
        metavar='QUERY',
        help=t("help_auto_option")
    )

    query_group.add_argument(
        '-A', '--analyze',
        dest='analyze_query',
        metavar='QUERY',
        help=t("help_analyze_option")
    )
    
    parser.add_argument(
        '--config',
        metavar='PATH',
        help=t("help_config_option")
    )

    parser.add_argument(
        '-new', '--new-terminal',
        dest='new_terminal',
        action='store_true',
        help=t("help_new_terminal")
    )

    parser.add_argument(
        '--auto-approve-all',
        dest='auto_approve_all',
        action='store_true',
        help=t("help_auto_approve_all")
    )

    parser.add_argument(
        '--auto-approve-commands',
        dest='auto_approve_commands',
        action='store_true',
        help=t("help_auto_approve_commands")
    )

    parser.add_argument(
        '--auto-approve-files',
        dest='auto_approve_files',
        action='store_true',
        help=t("help_auto_approve_files")
    )

    parser.add_argument(
        '--auto-approve-web',
        dest='auto_approve_web',
        action='store_true',
        help=t("help_auto_approve_web")
    )

    parser.add_argument(
        '--auto-max-steps',
        dest='auto_max_steps',
        type=int,
        help=t("help_auto_max_steps")
    )

    parser.add_argument(
        '-p', '--plan-file',
        dest='plan_file',
        metavar='PATH',
        help=t("help_plan_file")
    )

    
    parser.add_argument(
        '--ui-language',
        dest='ui_language',
        choices=['en', 'zh'],
        help=t("help_ui_language")
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.1.0',
        help=t("help_version")
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help=t("help_init")
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help=t("help_history")
    )
    
    parser.add_argument(
        '--clear-history',
        action='store_true',
        help=t("help_clear_history")
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help=t("help_test")
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
        print(t("error_initialization_failed", error=e), file=sys.stderr)
        sys.exit(1)
    
    if args.ui_language:
        aibash.set_language(args.ui_language)
        print(t("info_new_language", language=args.ui_language))
    
    # 查看历史记录
    if args.history:
        history_records = aibash.history_manager.load_records()
        if not history_records:
            print(t("history_none"))
        else:
            print(f"\n{t('history_total', count=len(history_records))}\n")
            print("=" * 80)
            for i, record in enumerate(history_records[-20:], 1):  # 显示最近20条
                timestamp = record.get('timestamp', '')
                user_query = record.get('user_query', '')
                command = record.get('command', '')
                success = record.get('success', True)
                output = record.get('output', '')
                
                print(f"\n[{i}] {timestamp}")
                if user_query:
                    print(t("history_query", query=user_query))
                print(t("history_command", command=command))
                status_text = t("history_status_success") if success else t("history_status_failed")
                print(t("history_status", status=status_text))
                if output:
                    output_preview = output[:100] + "..." if len(output) > 100 else output
                    print(t("history_output", output=output_preview))
                print("-" * 80)
        return
    
    # 清空历史记录
    if args.clear_history:
        confirm = input(t("history_clear_confirm")).strip().lower()
        if confirm == 'y':
            aibash.history_manager.clear_history()
            print(t("history_cleared"))
        else:
            print(t("common_operation_cancelled"))
        return
    
    # 测试连接
    if args.test:
        if not aibash.agent:
            aibash.terminal.error(t("error_agent_not_initialized"))
            aibash.terminal.info(t("info_run_init_first"))
            sys.exit(1)
        
        aibash.terminal.info(t("info_testing_connection"))
        if aibash.agent.test_connection():
            aibash.terminal.success(t("info_connection_success"))
            model_info = aibash.agent.get_model_info()
            aibash.terminal.info(t("info_connection_model", model=model_info.get('model', 'N/A')))
            aibash.terminal.info(t("info_connection_provider", provider=model_info.get('provider', 'N/A')))
        else:
            aibash.terminal.error(t("error_connection_failed"))
        return
    
    # 如果没有提供查询，显示帮助
    if not args.query and not args.auto_query and not args.analyze_query:
        parser.print_help()
        return
    
    # 检查 AI Agent 是否初始化
    if not aibash.agent:
        aibash.terminal.error("\n" + t("error_agent_not_initialized"))
        aibash.terminal.info(t("info_run_init_or_check"))
        sys.exit(1)
    
    plan_query_text: Optional[str] = None
    if args.plan_file:
        if not args.auto_query and not args.analyze_query:
            aibash.terminal.error(t("error_plan_requires_auto_mode"))
            sys.exit(1)
        file_path = Path(args.plan_file).expanduser()
        if not file_path.exists():
            aibash.terminal.error(t("error_auto_file_not_found", path=file_path))
            sys.exit(1)
        try:
            plan_query_text = file_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            aibash.terminal.error(t("error_auto_file_read", path=file_path, error=e))
            sys.exit(1)
        if not plan_query_text:
            aibash.terminal.error(t("error_plan_file_empty", path=file_path))
            sys.exit(1)
        aibash.terminal.info(t("info_auto_file_loaded", path=file_path))
    
    def collect_auto_options():
        auto_options = {}
        if args.auto_approve_all:
            auto_options['auto_confirm_all'] = True
        if args.auto_approve_commands:
            auto_options['auto_confirm_commands'] = True
        if args.auto_approve_files:
            auto_options['auto_confirm_files'] = True
        if args.auto_approve_web:
            auto_options['auto_confirm_web'] = True
        if args.auto_max_steps is not None:
            auto_options['max_steps'] = args.auto_max_steps
        return auto_options
    
    try:
        if args.analyze_query:
            analyze_query_text = plan_query_text if plan_query_text is not None else args.analyze_query
            if not analyze_query_text:
                aibash.terminal.error(t("error_analyze_missing_query"))
                sys.exit(1)
            auto_options = collect_auto_options()
            auto_options.setdefault('summary_workers', aibash.summary_workers)
            aibash.run_project_analysis(
                analyze_query_text,
                use_new_terminal=args.new_terminal,
                auto_options=auto_options
            )
            return
        
        if args.auto_query or plan_query_text is not None:
            auto_query_text = plan_query_text if plan_query_text is not None else (args.auto_query or "")
            if not auto_query_text:
                aibash.terminal.error(t("error_auto_missing_query"))
                sys.exit(1)
            auto_options = collect_auto_options()
            aibash.process_auto_task(
                auto_query_text,
                use_new_terminal=args.new_terminal,
                auto_options=auto_options
            )
        else:
            aibash.process_query(
                args.query,
                use_new_terminal=args.new_terminal
            )
    except KeyboardInterrupt:
        print("\n\n" + t("common_operation_cancelled"))
        sys.exit(0)
    except FileNotFoundError as e:
        print(t("error_file_not_found", error=e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(t("error_generic", error=e), file=sys.stderr)
        import traceback
        if '--debug' in sys.argv:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

