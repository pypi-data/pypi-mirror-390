"""技能注册表（阶段2）

- 聚合内置目录、用户目录与环境变量目录；
- 解析为 SkillMeta 列表，按 name 去重，过滤 `enabled=false`；
- 收集并提供冲突信息与解析错误摘要。
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .models import SkillMeta
from .loader import default_search_dirs, scan_metas


class SkillsRegistry:
    def __init__(self) -> None:
        self._metas: List[SkillMeta] = []
        self._errors: List[str] = []
        self._conflicts: Dict[str, List[str]] = {}

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    @property
    def conflicts(self) -> Dict[str, List[str]]:
        return {k: list(v) for k, v in self._conflicts.items()}

    def build(self) -> None:
        """构建注册表：扫描、过滤、去重，并记录冲突。"""
        search_dirs = default_search_dirs()
        metas, errors = scan_metas(search_dirs)
        self._errors = errors

        # 过滤 enabled=false
        metas = [m for m in metas if m.enabled]

        # 去重保持先到先得，记录冲突路径
        seen: Dict[str, SkillMeta] = {}
        conflicts: Dict[str, List[str]] = {}
        for m in metas:
            src = m.source_path or ""
            if m.name not in seen:
                seen[m.name] = m
                conflicts[m.name] = [src]
            else:
                # 记录冲突（不覆盖首个）
                conflicts[m.name].append(src)

        # 最终冲突字典仅保留存在多个来源的 name
        self._conflicts = {k: v for k, v in conflicts.items() if len(v) > 1}
        self._metas = list(seen.values())

    def list_metas(self) -> List[SkillMeta]:
        # 返回按名称排序的副本，保证展示稳定性
        return sorted(list(self._metas), key=lambda m: (m.name or ""))

    def find_meta(self, name: str) -> Optional[SkillMeta]:
        for m in self._metas:
            if m.name == name:
                return m
        return None

    def reload(self) -> None:
        self.build()

    def summary(self) -> str:
        """返回冲突与错误的摘要文本，供 CLI 或日志使用。"""
        lines: List[str] = []
        if self._errors:
            lines.append("[errors]")
            lines.extend(self._errors)
        if self._conflicts:
            lines.append("[conflicts]")
            for name, paths in self._conflicts.items():
                lines.append(f"重复 name '{name}':")
                for p in paths:
                    lines.append(f"  - {p}")
        return "\n".join(lines) if lines else ""