"""
项目摘要缓存

用于在项目目录下缓存文件摘要，避免重复生成，提升自动模式分析效率。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class ProjectSummaryCache:
    """项目摘要缓存"""

    CACHE_DIR_NAME = ".aibash_cache"
    CACHE_FILE_NAME = "summary_cache.json"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.cache_dir = self.root / self.CACHE_DIR_NAME
        self.cache_file = self.cache_dir / self.CACHE_FILE_NAME
        self._data: Dict[str, Dict[str, object]] = {}
        self._loaded = False

    def load(self) -> Dict[str, Dict[str, object]]:
        if self._loaded:
            return self._data
        if not self.cache_file.exists():
            self._data = {}
            self._loaded = True
            return self._data
        try:
            with self.cache_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                self._data = data.get("files", {})
        except Exception:
            self._data = {}
        self._loaded = True
        return self._data

    def save(self):
        if not self._loaded:
            return
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": "1.0",
                "files": self._data
            }
            with self.cache_file.open('w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_summary(self, file_path: Path, mtime: float) -> Optional[str]:
        data = self.load()
        key = self._make_key(file_path)
        entry = data.get(key)
        if not entry:
            return None
        if abs(entry.get("mtime", 0) - mtime) > 1e-6:
            return None
        return entry.get("summary") or None

    def update_summary(self, file_path: Path, mtime: float, summary: str):
        self.load()
        key = self._make_key(file_path)
        self._data[key] = {
            "mtime": mtime,
            "summary": summary
        }

    def _make_key(self, file_path: Path) -> str:
        try:
            return str(file_path.relative_to(self.root))
        except ValueError:
            return str(file_path.resolve())

