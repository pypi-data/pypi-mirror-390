"""
环境与项目上下文收集模块

用于在运行 AIBash 时收集系统、目录、Git 等信息，生成简洁的摘要，
供 Prompt 使用，帮助模型更好地理解当前工程环境。
"""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from typing import List


class ContextCollector:
    """上下文收集器"""

    def __init__(self, root: Path | None = None, max_dir_entries: int = 30):
        self.root = Path(root or Path.cwd())
        self.max_dir_entries = max_dir_entries

    def collect(self) -> str:
        """收集上下文并返回字符串摘要"""
        sections: List[str] = []

        sections.append(self._system_info_section())
        git_info = self._git_info_section()
        if git_info:
            sections.append(git_info)
        sections.append(self._directory_overview_section())
        env_info = self._environment_section()
        if env_info:
            sections.append(env_info)

        return "\n\n".join(sections)

    def _system_info_section(self) -> str:
        python_info = platform.python_version()
        implementation = platform.python_implementation()
        return "\n".join([
            "【System】",
            f"- Platform: {platform.system()} {platform.release()} ({platform.machine()})",
            f"- Python: {implementation} {python_info}",
            f"- Current working directory: {self.root}"
        ])

    def _git_info_section(self) -> str:
        git_dir = self.root / ".git"
        if not git_dir.exists():
            return ""
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except Exception:
            branch = "unknown"

        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except Exception:
            commit = "unknown"

        status = ""
        try:
            status_output = subprocess.check_output(
                ["git", "status", "--short"],
                cwd=self.root,
                stderr=subprocess.DEVNULL,
                text=True
            )
            changes = [line.strip() for line in status_output.strip().splitlines() if line.strip()]
            if changes:
                preview = "\n".join(f"  {entry}" for entry in changes[:10])
                suffix = "\n  ..." if len(changes) > 10 else ""
                status = f"- Pending changes ({len(changes)}):\n{preview}{suffix}"
            else:
                status = "- Pending changes: clean"
        except Exception:
            status = "- Pending changes: unavailable"

        return "\n".join([
            "【Git】",
            f"- Branch: {branch}",
            f"- Commit: {commit}",
            status
        ])

    def _directory_overview_section(self) -> str:
        entries: List[str] = []
        directories = []
        files = []

        try:
            for item in sorted(self.root.iterdir()):
                if item.name.startswith(".") and item.name not in {".env", ".env.local"}:
                    continue
                if item.is_dir():
                    directories.append(item)
                elif item.is_file():
                    files.append(item)
        except Exception:
            return "【Workspace】\n- Failed to list directory entries."

        entries.append("【Workspace】")
        entries.append(f"- Total directories: {len(directories)}")
        entries.append(f"- Total files: {len(files)}")

        def summarize_paths(paths: List[Path], label: str):
            if not paths:
                return
            entries.append(f"- {label}:")
            for path in paths[:self.max_dir_entries]:
                entries.append(f"  {path.name}/" if path.is_dir() else f"  {path.name}")
            if len(paths) > self.max_dir_entries:
                entries.append(f"  ... ({len(paths) - self.max_dir_entries} more)")

        summarize_paths(directories, "Top-level directories")
        summarize_paths(files, "Top-level files")

        # 统计常见文件类型
        ext_counter = {}
        for file_path in files:
            suffix = file_path.suffix.lower() or "<no-ext>"
            ext_counter[suffix] = ext_counter.get(suffix, 0) + 1
        if ext_counter:
            sorted_ext = sorted(ext_counter.items(), key=lambda kv: kv[1], reverse=True)
            preview = ", ".join(f"{ext}:{count}" for ext, count in sorted_ext[:10])
            entries.append(f"- File extensions (top): {preview}")

        return "\n".join(entries)

    def _environment_section(self) -> str:
        keys_of_interest = [
            "SHELL", "TERM", "VIRTUAL_ENV", "CONDA_DEFAULT_ENV", "PYTHONPATH",
            "PWD", "EDITOR", "VISUAL"
        ]
        env_items = []
        for key in keys_of_interest:
            value = os.environ.get(key)
            if value:
                env_items.append(f"- {key}={value}")
        if not env_items:
            return ""
        return "【Environment Variables】\n" + "\n".join(env_items)

