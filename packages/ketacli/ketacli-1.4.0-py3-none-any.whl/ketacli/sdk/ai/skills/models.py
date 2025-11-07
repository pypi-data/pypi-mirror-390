"""阶段1将实现具体数据模型；此处提供占位与类型别名。

阶段0目标仅确保包可导入，无具体逻辑。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SkillMeta:
    name: str
    summary: Optional[str] = None
    enabled: bool = True
    triggers: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    tools_whitelist: Optional[List[str]] = None
    source_path: Optional[str] = None


@dataclass
class Skill:
    meta: SkillMeta
    description: Optional[str] = None