"""
命令历史记录模块

保存和加载命令执行历史
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, history_file: str, max_records: int = 50, enabled: bool = True):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
            max_records: 最大记录数
            enabled: 是否启用历史记录
        """
        self.history_file = Path(history_file)
        self.max_records = max_records
        self.enabled = enabled
        
        # 确保目录存在
        if self.history_file.parent:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def add_record(
        self,
        command: str,
        output: str = "",
        success: bool = True,
        user_query: str = ""
    ):
        """
        添加历史记录
        
        Args:
            command: 执行的命令
            output: 命令输出
            success: 是否成功
            user_query: 原始用户查询
        """
        if not self.enabled:
            return
        
        try:
            records = self.load_records()
            
            record = {
                'timestamp': datetime.now().isoformat(),
                'user_query': user_query,
                'command': command,
                'output': output,
                'success': success
            }
            
            records.append(record)
            
            # 限制记录数量
            if len(records) > self.max_records:
                records = records[-self.max_records:]
            
            self._save_records(records)
        except Exception as e:
            # 静默失败，不影响主流程
            pass
    
    def load_records(self) -> List[Dict[str, Any]]:
        """
        加载历史记录
        
        Returns:
            历史记录列表
        """
        if not self.enabled or not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('records', [])
        except Exception:
            return []
    
    def _save_records(self, records: List[Dict[str, Any]]):
        """保存历史记录"""
        try:
            data = {
                'version': '1.0',
                'records': records
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def clear_history(self):
        """清空历史记录"""
        if self.history_file.exists():
            try:
                self.history_file.unlink()
            except Exception:
                pass
    
    def get_recent_records(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的记录
        
        Args:
            count: 记录数量
            
        Returns:
            最近的记录列表
        """
        records = self.load_records()
        return records[-count:] if len(records) > count else records

